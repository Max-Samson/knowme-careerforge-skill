#!/usr/bin/env node
// Independent real-browser canvas check. No rendering pipeline dependencies.
// Usage: node tests/templates/check_canvas_browser.cjs /tmp/canvas-review
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const output = path.resolve(process.argv[2] || '/tmp/careerforge-canvas-review');
fs.mkdirSync(output, { recursive: true });
const templates = fs.readdirSync(path.join(root, 'src/templates')).filter(name => fs.existsSync(path.join(root, 'src/templates', name, 'metadata.json')));
const cases = ['zh', 'en', 'education-stress'];
function fixture(scenario) {
  const en = scenario !== 'zh';
  const stress = scenario === 'education-stress';
  return {
    language: en ? 'en-US' : 'zh-CN',
    basics: {
      name: en ? 'Canvas Test Candidate' : '画布测试候选人',
      title: en ? 'Software Engineer' : '软件工程师',
      email: 'canvas-test@example.invalid', phone: '+00 000 000 0000',
      location: en ? 'Test City' : '测试城市',
      summary: en ? 'Synthetic layout fixture for verifying text wrapping and section visibility.' : '合成布局测试数据，用于验证文字换行、章节显示与教育经历完整性。'
    },
    skills: [{ category: en ? 'Engineering' : '工程技术', items: ['Python', 'TypeScript', 'SQL', 'Distributed systems'] }, { category: en ? 'Tools' : '开发工具', items: ['Git', 'Linux', 'Docker'] }],
    experience: Array.from({ length: 2 }, (_, i) => ({ company: en ? `Test Organization ${i + 1}` : `测试组织 ${i + 1}`, role: en ? 'Engineer' : '工程师', startDate: '2020-01', endDate: '2022-12', bullets: [{ text: en ? 'Built a synthetic demonstration service to exercise long bullet wrapping in the canvas.' : '构建演示服务，用于检查较长条目文本在画布中的自动换行。' }, { text: en ? 'Collaborated on test documentation and release checks.' : '参与测试文档与发布检查。' }] })),
    projects: [{ name: en ? 'Layout Demonstration Project' : '布局演示项目', role: en ? 'Developer' : '开发者', techStack: ['Python', 'TypeScript'], bullets: [{ text: en ? 'Verified that every supplied fact remains visible.' : '验证所有提供的事实均完整显示。' }] }],
    education: Array.from({ length: stress ? 5 : 3 }, (_, i) => ({
      institution: en ? `Test University ${i + 1}${stress ? ' — International Graduate School of Computing and Information Sciences' : ''}` : `测试大学 ${i + 1}`,
      degree: en ? 'Master of Science' : '硕士', field: en ? 'Computer Science' : '计算机科学',
      startDate: '2016-09', endDate: '2019-06',
      summary: stress ? 'Synthetic education detail: research, collaborative seminars, and a long thesis title used to check wrapping without clipping or reducing font size.' : en ? 'Synthetic education record.' : '合成教育记录。'
    })),
    certifications: [en ? 'Synthetic Test Certificate' : '合成测试证书']
  };
}
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1050, height: 1300 }, deviceScaleFactor: 1 });
  const results = [];
  try {
    for (const scenario of cases) {
      const profile = path.join(output, `${scenario}.json`);
      fs.writeFileSync(profile, JSON.stringify(fixture(scenario)));
      for (const template of templates) {
        const html = path.join(output, `${scenario}-${template}.html`);
        const inst = spawnSync('python3', [path.join(root, 'scripts/template/instantiate-resume.py'), '-t', template, '-p', profile, '-o', html, '--quiet'], { encoding: 'utf8' });
        if (inst.status !== 0) throw new Error(inst.stdout + inst.stderr);
        if (JSON.parse(inst.stdout).status !== 'PASS') throw new Error(inst.stdout);
        await page.goto(pathToFileURL(html).href);
        await page.evaluate(() => document.fonts.ready);
        for (const media of ['screen', 'print']) {
          await page.emulateMedia({ media });
          const measured = await page.evaluate(() => {
            const canvas = document.querySelector('.resume-page');
            const box = canvas.getBoundingClientRect();
            const errors = [];
            const walker = document.createTreeWalker(canvas, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
              const node = walker.currentNode;
              if (!node.textContent.trim()) continue;
              const range = document.createRange(); range.selectNodeContents(node);
              for (const rect of range.getClientRects()) {
                if (rect.left < box.left - 1 || rect.right > box.right + 1 || rect.top < box.top - 1 || rect.bottom > box.bottom + 1) errors.push('Text outside canvas: ' + node.textContent.slice(0, 70));
                for (let parent = node.parentElement; parent && parent !== canvas; parent = parent.parentElement) {
                  const style = getComputedStyle(parent), r = parent.getBoundingClientRect();
                  if (/(hidden|clip|auto|scroll)/.test(style.overflowX) && (rect.left < r.left - 1 || rect.right > r.right + 1)) errors.push('Horizontal clipping: ' + parent.className);
                  if (/(hidden|clip|auto|scroll)/.test(style.overflowY) && (rect.top < r.top - 1 || rect.bottom > r.bottom + 1)) errors.push('Vertical clipping: ' + parent.className);
                }
              }
            }
            const education = [...document.querySelectorAll('.education-item')].map(el => {
              const r = el.getBoundingClientRect();
              if (el.closest('aside')) errors.push('Education placed in narrow sidebar');
              if (r.width < box.width * 0.40) errors.push('Education column too narrow');
              return { width: r.width, height: r.height, top: r.top, bottom: r.bottom };
            });
            for (let i = 1; i < education.length; i++) if (education[i].top < education[i - 1].bottom - 1) errors.push('Education entries overlap');
            return { errors: [...new Set(errors)], width: box.width, height: box.height, education };
          });
          if (measured.education.length !== (scenario === 'education-stress' ? 5 : 3)) measured.errors.push('Education missing');
          results.push({ scenario, template, media, ...measured });
          if (media === 'screen') await page.screenshot({ path: path.join(output, `${scenario}-${template}.png`), fullPage: true });
        }
      }
    }
    // Browser-rendered contact sheets make all ten designs reviewable together.
    for (const scenario of cases) {
      const gallery = path.join(output, `${scenario}-gallery.html`);
      fs.writeFileSync(gallery, `<html><body style="margin:16px;display:grid;grid-template-columns:repeat(5,1fr);gap:12px;font:16px sans-serif;background:#ddd">${templates.map(t => `<div><h3>${t}</h3><img style="width:100%" src="${scenario}-${t}.png"></div>`).join('')}</body></html>`);
      await page.emulateMedia({ media: 'screen' });
      await page.setViewportSize({ width: 2100, height: 1600 });
      await page.goto(pathToFileURL(gallery).href);
      await page.screenshot({ path: path.join(output, `${scenario}-gallery.png`), fullPage: true });
    }
    const report = { browser: browser.version(), checks: results.length, failures: results.filter(r => r.errors.length), results };
    fs.writeFileSync(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ output, checks: report.checks, failures: report.failures }, null, 2));
    if (report.failures.length) process.exitCode = 1;
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
