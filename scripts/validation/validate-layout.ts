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
    actualHeightPx: number;
    allowedHeightPx: number;
    isOverflow: boolean;
    overflowDeltaPx: number;
  }>;
  overflowSections: Array<{
    selector: string;
    bottomPx: number;
    overflowByPx: number;
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
    deviceScaleFactor: 1
  });

  const page = await context.newPage();
  await page.goto(`file://${absoluteHtml}`, { waitUntil: 'networkidle' });
  await page.evaluateHandle('document.fonts.ready');

  // A4 标准高度 (297mm in pixels at 96 DPI ~= 1122.5px)
  const A4_HEIGHT_PX = 1122.5;

  const evaluation = await page.evaluate((allowedHeight) => {
    const pages = Array.from(document.querySelectorAll('.resume-page'));
    const details = pages.map((p, idx) => {
      const rect = p.getBoundingClientRect();
      const actualHeight = Math.ceil(rect.height);
      const isOverflow = actualHeight > allowedHeight + 2; // 2px 浮点容差
      return {
        pageIndex: idx + 1,
        actualHeightPx: actualHeight,
        allowedHeightPx: allowedHeight,
        isOverflow,
        overflowDeltaPx: isOverflow ? Math.ceil(actualHeight - allowedHeight) : 0
      };
    });

    const overflowSections: Array<{ selector: string; bottomPx: number; overflowByPx: number }> = [];
    if (details.some(d => d.isOverflow)) {
      const items = Array.from(document.querySelectorAll('.experience-item, .project-item, .skills-content, .resume-section'));
      for (const item of items) {
        const rect = item.getBoundingClientRect();
        if (rect.bottom > allowedHeight) {
          overflowSections.push({
            selector: item.className ? `.${item.className.split(' ').join('.')}` : item.tagName.toLowerCase(),
            bottomPx: Math.ceil(rect.bottom),
            overflowByPx: Math.ceil(rect.bottom - allowedHeight)
          });
        }
      }
    }

    return {
      totalPagesFound: pages.length || 1,
      pageDetails: details.length ? details : [{
        pageIndex: 1,
        actualHeightPx: Math.ceil(document.body.getBoundingClientRect().height),
        allowedHeightPx: allowedHeight,
        isOverflow: document.body.getBoundingClientRect().height > allowedHeight + 2,
        overflowDeltaPx: Math.max(0, Math.ceil(document.body.getBoundingClientRect().height - allowedHeight))
      }],
      overflowSections
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
    } else if (!args[i].startsWith('-')) {
      htmlPath = args[i];
    }
  }

  try {
    const result = await validateLayout(htmlPath, expectedPages);

    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
      process.exit(result.status === 'PASS' ? 0 : 1);
    }

    console.log('======================================================');
    console.log(`  KnowMe CareerForge — Layout QA: ${result.status}`);
    console.log(`  HTML Path      : ${htmlPath}`);
    console.log(`  Expected Pages : ${result.expectedPages} | Pages Found: ${result.totalPagesFound}`);
    console.log('------------------------------------------------------');

    for (const p of result.pageDetails) {
      const fitText = p.isOverflow ? `[✗ OVERFLOW by ${p.overflowDeltaPx}px]` : `[✓ FIT] (Overflow: ${p.overflowDeltaPx}px)`;
      console.log(`  Page ${p.pageIndex}: ${p.actualHeightPx}px / ${p.allowedHeightPx}px ${fitText}`);
    }

    if (result.overflowSections.length > 0) {
      console.log('\n[!] Offending Overflow Elements:');
      for (const el of result.overflowSections.slice(0, 3)) {
        console.log(`  - Element "${el.selector}" exceeds A4 baseline by ${el.overflowByPx}px (Bottom: ${el.bottomPx}px)`);
      }
      console.log('\n💡 Recommendation: Reduce --resume-space-section by 1~2pt or reduce --resume-font-size-body by 0.2pt in <style>.');
    }

    console.log('======================================================');
    process.exit(result.status === 'PASS' ? 0 : 1);
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[✗] Layout Validation Failed: ${errorMsg}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
