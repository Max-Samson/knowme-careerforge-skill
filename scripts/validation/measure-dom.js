#!/usr/bin/env node
/**
 * KnowMe CareerForge — Fast Headless DOM Measurement Engine
 * 精确测量 HTML 简历工作区的物理渲染高度 (px) 与溢出 DOM 节点。
 */

const fs = require('fs');
const path = require('path');

function findSystemBrowser() {
  const customBin = process.env.CHROME_BIN || process.env.BROWSER_PATH;
  if (customBin && fs.existsSync(customBin)) return customBin;

  const candidates = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
  ];

  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

async function run() {
  const targetHtml = process.argv[2] || 'workspace/resume.html';
  const absPath = path.resolve(targetHtml);

  if (!fs.existsSync(absPath)) {
    console.error(JSON.stringify({ error: `File not found: ${absPath}` }));
    process.exit(1);
  }

  let pw;
  try {
    pw = require('playwright-core');
  } catch {
    try {
      pw = require('playwright');
    } catch (e) {
      console.error(JSON.stringify({ error: 'Playwright engine not installed' }));
      process.exit(2);
    }
  }

  const browserBin = findSystemBrowser();
  const launchOptions = {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  };
  if (browserBin) {
    launchOptions.executablePath = browserBin;
  }

  let browser;
  try {
    browser = await pw.chromium.launch(launchOptions);
  } catch (err) {
    console.error(JSON.stringify({ error: `Failed to launch browser: ${err.message}` }));
    process.exit(3);
  }

  try {
    const page = await browser.newPage({
      viewport: { width: 794, height: 1123 }
    });

    await page.goto(`file://${absPath}`, { waitUntil: 'load' });
    try {
      await page.evaluateHandle('document.fonts.ready');
    } catch {}

    const evalResult = await page.evaluate(() => {
      const pageElem = document.querySelector('.resume-page');
      if (pageElem) {
        pageElem.style.overflow = 'visible';
        pageElem.style.height = 'auto';
        pageElem.style.minHeight = '0px';
        pageElem.style.maxHeight = 'none';
      }
      const actualHeight = Math.ceil(pageElem ? pageElem.getBoundingClientRect().height : document.body.getBoundingClientRect().height);

      const overflowItems = [];
      if (actualHeight > 1122.5) {
        const checkItems = Array.from(document.querySelectorAll('.experience-item, .project-item, .education-item, .skills-content, .resume-section, .bullet-list li'));
        for (const item of checkItems) {
          const r = item.getBoundingClientRect();
          if (r.bottom > 1122.5) {
            const sel = item.id ? `#${item.id}` : (item.className ? `.${item.className.split(' ').filter(Boolean).join('.')}` : item.tagName.toLowerCase());
            overflowItems.push({
              selector: sel,
              bottomPx: Math.ceil(r.bottom),
              overflowByPx: Math.ceil(r.bottom - 1122.5)
            });
          }
        }
      }

      return {
        actualHeightPx: actualHeight,
        overflowItems: overflowItems.slice(0, 5)
      };
    });

    await browser.close();
    console.log(JSON.stringify(evalResult));
  } catch (err) {
    if (browser) await browser.close();
    console.error(JSON.stringify({ error: err.message }));
    process.exit(4);
  }
}

run();
