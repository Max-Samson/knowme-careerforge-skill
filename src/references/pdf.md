# Reference Manual: Deterministic PDF Rendering (Playwright 确定性渲染实践)

---

## 1. 为什么使用 Playwright 而非传统转换器？

传统 HTML 到 PDF 工具（如 wkhtmltopdf 或 puppeteer 简易打印）存在两大痛点：
1. **网络字体未就绪即打印**：导致字体 fallback 变形，字符间距和总高度发生突变；
2. **跨系统渲染差异**：Linux / macOS / Windows 默认 DPI 与字体抗锯齿不同。

---

## 2. Playwright 确定性渲染标准配置

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 794, height: 1123 }, // A4 at 96 DPI
  deviceScaleFactor: 2
});

const page = await context.newPage();
await page.goto(fileUrl, { waitUntil: 'networkidle' });

// 严格等待所有 Web 字体与静态资源加载完成
await page.evaluateHandle('document.fonts.ready');

// 导出标准 A4 矢量 PDF
await page.pdf({
  path: outputPath,
  format: 'A4',
  printBackground: true,
  preferCSSPageSize: true,
  margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' }
});

await browser.close();
```
