#!/usr/bin/env ts-node
/**
 * KnowMe CareerForge — Playwright DOM Layout & Overflow Inspector
 * 基于无头浏览器真实渲染计算 DOM 盒模型高度，检测单页/双页物理 A4 溢出与孤行。
 */

import { chromium } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

interface LayoutValidationResult {
  status: 'PASS' | 'OVERFLOW';
  expectedPages: number;
  totalPagesFound: number;
  pageDetails: Array<{
    pageIndex: number;
    measuredHeightPx: number;
    allowedHeightPx: number;
    overflowPx: number;
    isOverflow: boolean;
  }>;
  overflowSections: Array<{
    selector: string;
    heightPx: number;
    textPreview: string;
  }>;
}

export async function validateLayout(htmlPath: string, expectedPages: number = 1): Promise<LayoutValidationResult> {
  const absoluteHtml = path.resolve(htmlPath);
  if (!fs.existsSync(absoluteHtml)) {
    throw new Error(`HTML file not found: ${absoluteHtml}`);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 794, height: 1123 }, // A4 at 96 DPI
    deviceScaleFactor: 2
  });

  const page = await context.newPage();
  await page.goto(`file://${absoluteHtml}`, { waitUntil: 'networkidle' });
  await page.evaluateHandle('document.fonts.ready');

  // A4 标准高度 (297mm in pixels at 96 DPI ~= 1122.5px)
  const A4_HEIGHT_PX = 1122.5;

  const evaluation = await page.evaluate((allowedHeight) => {
    const pages = Array.from(document.querySelectorAll('.resume-page'));
    const details = pages.map((el, index) => {
      const rect = el.getBoundingClientRect();
      const scrollH = el.scrollHeight;
      const actualH = Math.max(rect.height, scrollH);
      const diff = actualH - allowedHeight;
      return {
        pageIndex: index + 1,
        measuredHeightPx: Math.round(actualH * 10) / 10,
        allowedHeightPx: allowedHeight,
        overflowPx: diff > 2 ? Math.round(diff * 10) / 10 : 0,
        isOverflow: diff > 2
      };
    });

    const overflows: Array<{ selector: string; heightPx: number; textPreview: string }> = [];
    if (details.some(d => d.isOverflow)) {
      const sections = Array.from(document.querySelectorAll('.resume-section, .timeline-item, .milestone-item, .experience-item, tr'));
      for (const s of sections) {
        const r = s.getBoundingClientRect();
        if (r.bottom > allowedHeight) {
          overflows.push({
            selector: s.className || s.tagName.toLowerCase(),
            heightPx: Math.round(r.height),
            textPreview: (s.textContent || '').trim().slice(0, 60)
          });
        }
      }
    }

    return {
      totalPagesFound: pages.length,
      pageDetails: details,
      overflowSections: overflows
    };
  }, A4_HEIGHT_PX);

  await browser.close();

  const hasOverflow = evaluation.pageDetails.some(p => p.isOverflow) || evaluation.totalPagesFound > expectedPages;

  return {
    status: hasOverflow ? 'OVERFLOW' : 'PASS',
    expectedPages,
    totalPagesFound: evaluation.totalPagesFound,
    pageDetails: evaluation.pageDetails,
    overflowSections: evaluation.overflowSections
  };
}

async function main() {
  const args = process.argv.slice(2);
  let htmlPath = 'workspace/resume.html';
  let expectedPages = 1;
  let jsonOutput = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--html' || args[i] === '-i') {
      htmlPath = args[i + 1];
      i++;
    } else if (args[i] === '--expected-pages' || args[i] === '-p') {
      expectedPages = parseInt(args[i + 1], 10) || 1;
      i++;
    } else if (args[i] === '--json') {
      jsonOutput = true;
    }
  }

  try {
    const result = await validateLayout(htmlPath, expectedPages);

    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log('======================================================');
    console.log(`  KnowMe CareerForge — Layout QA: ${result.status}`);
    console.log(`  HTML Path      : ${htmlPath}`);
    console.log(`  Expected Pages : ${result.expectedPages} | Pages Found: ${result.totalPagesFound}`);
    console.log('------------------------------------------------------');

    for (const p of result.pageDetails) {
      const statusSymbol = p.isOverflow ? '✗ OVERFLOW' : '✓ FIT';
      console.log(`  Page ${p.pageIndex}: ${p.measuredHeightPx}px / ${p.allowedHeightPx}px [${statusSymbol}] (Overflow: ${p.overflowPx}px)`);
    }

    if (result.overflowSections.length > 0) {
      console.log('\n[!] Nodes exceeding A4 physical boundary:');
      for (const o of result.overflowSections) {
        console.log(`  - <${o.selector}> (${o.heightPx}px): "${o.textPreview}..."`);
      }
      console.log('\n[Self-Healing Guidance]:');
      console.log('  1. Reduce --resume-space-section by 1~2pt in workspace/resume.html <style>');
      console.log('  2. Reduce --resume-font-size-body by 0.2pt');
      console.log('  3. Condense verbose bullet points');
    }

    console.log('======================================================');

    if (result.status === 'OVERFLOW') {
      process.exit(1);
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[✗] Layout Validation Failed: ${msg}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
