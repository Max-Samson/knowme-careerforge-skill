#!/usr/bin/env ts-node
/**
 * KnowMe CareerForge — Playwright Deterministic PDF Renderer
 * 加载自包含 HTML 中间工作区，等待字体及样式准备就绪，输出标准像素级 A4 PDF。
 */

import { chromium } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

interface RenderOptions {
  inputHtml: string;
  outputPdf: string;
}

export async function renderResumePdf(options: RenderOptions): Promise<void> {
  const absoluteHtml = path.resolve(options.inputHtml);
  const absolutePdf = path.resolve(options.outputPdf);

  if (!fs.existsSync(absoluteHtml)) {
    throw new Error(`Input HTML file does not exist: ${absoluteHtml}`);
  }

  const outputDir = path.dirname(absolutePdf);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('======================================================');
  console.log('  KnowMe CareerForge — Playwright PDF Renderer');
  console.log(`  Source Canvas : ${absoluteHtml}`);
  console.log(`  Target PDF    : ${absolutePdf}`);
  console.log('======================================================');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 794, height: 1123 }, // A4 at 96 DPI
    deviceScaleFactor: 2
  });

  const page = await context.newPage();
  await page.goto(`file://${absoluteHtml}`, { waitUntil: 'networkidle' });
  await page.evaluateHandle('document.fonts.ready');

  await page.pdf({
    path: absolutePdf,
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' }
  });

  await browser.close();
  console.log(`[✓] Deterministic PDF Rendered Successfully -> ${absolutePdf}`);
}

async function main() {
  const args = process.argv.slice(2);
  let inputHtml = 'workspace/resume.html';
  let outputPdf = 'workspace/resume.pdf';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' || args[i] === '-i') {
      inputHtml = args[i + 1];
      i++;
    } else if (args[i] === '--output' || args[i] === '-o') {
      outputPdf = args[i + 1];
      i++;
    } else if (!args[i].startsWith('-')) {
      if (i === 0) inputHtml = args[i];
      else if (i === 1) outputPdf = args[i];
    }
  }

  try {
    await renderResumePdf({ inputHtml, outputPdf });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[✗] PDF Rendering Failed: ${errorMsg}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
