'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { run, reduceTokens, missingText } = require('../../scripts/rendering/browser-engine');
const { PDFDocument } = require('pdf-lib');
const playwright = require('playwright');

const css = '@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0}.resume-page{width:210mm;height:297mm;position:relative;break-after:page;padding:12mm;font:12pt Arial}.resume-page:last-child{break-after:auto}';
const page = text => `<article class="resume-page">${text === 'Bob' ? `<h2>${text}</h2>` : `<h1 class="candidate-name">${text}</h1>`}<p>Education University 2020 2024</p></article>`;
async function fixture(t, body = page('Alice'), extra = '') {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'resume-engine-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const html = path.join(dir, 'resume with space #名.html');
  const pdf = path.join(dir, 'resume.pdf');
  await fs.writeFile(html, `<html><head><meta charset="utf-8"><style>${css}${extra}</style></head><body>${body}</body></html>`);
  return { dir, html, pdf };
}
function pass(r) { assert.equal(r.status, 'PASS', JSON.stringify(r.errors)); }
async function patchPdf(t, mutate) {
  const launch = playwright.chromium.launch;
  playwright.chromium.launch = async function (...args) {
    const browser = await launch.apply(this, args);
    const newPage = browser.newPage.bind(browser);
    browser.newPage = async (...args) => {
      const page = await newPage(...args);
      const pdf = page.pdf.bind(page);
      page.pdf = async (...args) => mutate(await pdf(...args));
      return page;
    };
    return browser;
  };
  t.after(() => { playwright.chromium.launch = launch; });
}

test('normalization counts duplicate characters; token ladder never increases or inserts', () => {
  assert.equal(missingText('Ａlice 教育 教育', 'Alice教育'), '教育');
  const html = '<style>:root{--resume-space-section: 2pt;--resume-font-size-body: 8pt;}</style>';
  assert.equal(reduceTokens(html, { '--resume-space-section': '8.5pt', '--resume-font-size-body': '8.8pt', '--new': '1pt' }).content, html);
});
test('fresh two-page PDF and every-page text inspection', async t => {
  const f = await fixture(t, page('Alice') + page('Bob'));
  await fs.writeFile(f.pdf, 'OLD');
  const r = await run(f.html, { expectedPages: 2, outputPdf: f.pdf });
  pass(r);
  assert.equal(r.checks.pdf.pageCount, 2);
  assert.match(r.checks.text.pages[1].text, /Bob/);
  assert.equal((await PDFDocument.load(await fs.readFile(f.pdf))).getPageCount(), 2);
});
for (const [name, body, extra] of [
  ['above', page('Alice') + '', 'h1{position:absolute;top:-80px}'],
  ['left', page('Alice'), 'h1{position:absolute;left:-80px}'],
  ['right', page('Alice'), 'h1{position:absolute;left:780px;white-space:nowrap}'],
  ['bottom', page('Alice'), 'h1{position:absolute;top:1100px}'],
  ['ancestor', '<div style="height:60px;overflow:hidden">' + page('Alice') + '</div>', ''],
  ['nested clipping', '<article class="resume-page"><div style="height:10px;overflow:hidden"><p>Education University 2020</p></div></article>', ''],
  ['second page', page('Alice') + page('Bob'), '.resume-page:nth-child(2) h2{position:absolute;left:-60px}'],
  ['print media', page('Alice'), '@media print{h1{position:absolute;left:-80px}}'],
  ['no page', '<h1>Alice</h1>', ''],
  ['wrong paper', page('Alice'), '@page{size:Letter}'],
  ['blank', '<article class="resume-page"></article>', '']
]) test(`reject ${name} and preserve existing output/source`, async t => {
  const f = await fixture(t, body, extra);
  const original = await fs.readFile(f.html);
  await fs.writeFile(f.pdf, 'OLD');
  const r = await run(f.html, { expectedPages: name === 'second page' ? 2 : 1, outputPdf: f.pdf });
  assert.equal(r.status, 'FAIL', JSON.stringify(r.errors));
  assert.equal(await fs.readFile(f.pdf, 'utf8'), 'OLD');
  assert.deepEqual(await fs.readFile(f.html), original);
});
test('one page passes with a two-page upper limit', async t => {
  const f = await fixture(t);
  pass(await run(f.html, { expectedPages: 2 }));
});
test('all PDF page sizes checked including page two', async t => {
  const f = await fixture(t, page('Alice') + page('Bob'));
  await patchPdf(t, async bytes => {
    const pdf = await PDFDocument.load(bytes); pdf.getPage(1).setSize(500, 700); return Buffer.from(await pdf.save());
  });
  const r = await run(f.html, { expectedPages: 2 });
  assert.equal(r.checks.pdf.status, 'FAIL');
});
test('parseable PDF missing education text cannot pass', async t => {
  const f = await fixture(t);
  await patchPdf(t, async () => {
    const pdf = await PDFDocument.create(); pdf.addPage([595.276, 841.89]).drawText('Alice'); return Buffer.from(await pdf.save());
  });
  const r = await run(f.html);
  assert.equal(r.checks.pdf.status, 'PASS');
  assert.equal(r.checks.text.status, 'FAIL');
  assert.match(r.checks.text.pages[0].missing, /Education/);
  assert.ok(r.checks.text.pages[0].missingCodepoints.some(item => item.character === 'E' && item.codepoint === 'U+0045'));
});
test('PDF generation failure is UNVERIFIED and preserves old PDF', async t => {
  const f = await fixture(t); await fs.writeFile(f.pdf, 'OLD');
  await patchPdf(t, async () => { throw new Error('injected print failure'); });
  const r = await run(f.html, { outputPdf: f.pdf });
  assert.equal(r.status, 'UNVERIFIED');
  assert.equal(await fs.readFile(f.pdf, 'utf8'), 'OLD');
});
const healCSS = ':root{--resume-space-section:22pt;--resume-space-item:2pt;--resume-font-size-body:8pt} .stack{height:1020px;margin-bottom:var(--resume-space-section)}';
const healBody = '<article class="resume-page"><h1 class="candidate-name" style="margin:0;font-size:12pt;line-height:18px">Alice</h1><div class="stack">Education University 2020 2024</div><div>End</div></article>';
test('autoheal commits only a fully verified reduction', async t => {
  const f = await fixture(t, healBody, healCSS);
  const before = await fs.readFile(f.html, 'utf8');
  assert.equal((await run(f.html)).status, 'FAIL');
  const r = await run(f.html, { autoHeal: true, outputPdf: f.pdf });
  pass(r);
  assert.equal(r.checks.auto_heal.committed, true);
  assert.notEqual(await fs.readFile(f.html, 'utf8'), before);
  assert.match(await fs.readFile(f.html, 'utf8'), /--resume-font-size-body:8pt/);
});
test('exhausted autoheal leaves source unchanged', async t => {
  const f = await fixture(t, healBody, healCSS + '.stack{height:1800px}');
  const before = await fs.readFile(f.html);
  const r = await run(f.html, { autoHeal: true });
  assert.equal(r.status, 'FAIL');
  assert.deepEqual(await fs.readFile(f.html), before);
  assert.equal(r.checks.auto_heal.committed, false);
  assert.deepEqual((await fs.readdir(f.dir)).sort(), [path.basename(f.html)]);
});
test('publication failure rolls back successful autoheal', async t => {
  const f = await fixture(t, healBody, healCSS);
  const before = await fs.readFile(f.html);
  await fs.writeFile(f.pdf, 'OLD');
  const rename = fs.rename;
  fs.rename = async (src, dest) => { if (dest === f.pdf) throw new Error('injected rename failure'); return rename(src, dest); };
  t.after(() => { fs.rename = rename; });
  const r = await run(f.html, { autoHeal: true, outputPdf: f.pdf });
  assert.equal(r.status, 'FAIL');
  assert.ok(r.checks.auto_heal.iterations > 0);
  assert.deepEqual(await fs.readFile(f.html), before);
  assert.equal(await fs.readFile(f.pdf, 'utf8'), 'OLD');
});
test('CLI exits FAIL=1 and UNVERIFIED=2 with pure JSON across Python/JS/TS', async t => {
  const f = await fixture(t);
  for (const [exe, args] of [
    ['node', ['scripts/rendering/browser-engine.js']],
    ['node', ['scripts/validation/measure-dom.js']],
    ['python3', ['scripts/rendering/render-pdf.py']],
    ['python3', ['scripts/validation/validate-resume.py']],
    ['node', ['-r', 'ts-node/register', 'scripts/rendering/render-pdf.ts']],
    ['node', ['-r', 'ts-node/register', 'scripts/validation/validate-layout.ts']],
    ['node', ['-r', 'ts-node/register', 'scripts/validation/validate-ats.ts']]
  ]) {
    for (const [html, status, code] of [[path.join(f.dir, 'missing'), 'FAIL', 1], [f.html, 'UNVERIFIED', 2]]) {
      const p = spawnSync(exe, [...args, html], { encoding: 'utf8', env: { ...process.env, CHROME_BIN: '/missing-browser' } });
      assert.equal(p.status, code, p.stderr);
      assert.equal(JSON.parse(p.stdout).status, status, p.stdout);
    }
  }
});
test('font loading failure cannot be ignored', async t => {
  const f = await fixture(t, page('Alice'), '@font-face{font-family:Broken;src:url(missing.woff2)}h1{font-family:Broken}');
  const r = await run(f.html, { outputPdf: f.pdf });
  assert.equal(r.status, 'UNVERIFIED');
  assert.equal(r.checks.fonts.status, 'UNVERIFIED');
  await assert.rejects(fs.stat(f.pdf), { code: 'ENOENT' });
});
test('same characters with scrambled name do not pass text verification', async t => {
  const f = await fixture(t);
  await patchPdf(t, async () => {
    const pdf = await PDFDocument.create();
    pdf.addPage([595.276, 841.89]).drawText('ecilA Education University 2020 2024');
    return Buffer.from(await pdf.save());
  });
  const r = await run(f.html);
  assert.equal(r.checks.text.status, 'FAIL');
  assert.ok(r.checks.text.pages[0].missingFragments.includes('Alice'));
});
test('missing dependency returns pure JSON UNVERIFIED without stale-PDF success', async t => {
  const f = await fixture(t); await fs.writeFile(f.pdf, 'OLD');
  const preload = path.join(f.dir, 'missing.cjs');
  await fs.writeFile(preload, `const Module=require('node:module');const load=Module._load;Module._load=function(id,...args){if(id==='pdf-lib')throw new Error('injected missing pdf-lib');return load.call(this,id,...args)};`);
  const p = spawnSync('node', ['-r', preload, 'scripts/rendering/browser-engine.js', f.html, '--output', f.pdf], { encoding: 'utf8' });
  assert.equal(p.status, 2);
  assert.equal(JSON.parse(p.stdout).status, 'UNVERIFIED');
  assert.equal(await fs.readFile(f.pdf, 'utf8'), 'OLD');
});
test('autoheal cannot publish when PDF text remains missing', async t => {
  const f = await fixture(t, healBody, healCSS);
  const before = await fs.readFile(f.html);
  await fs.writeFile(f.pdf, 'OLD');
  await patchPdf(t, async () => {
    const pdf = await PDFDocument.create(); pdf.addPage([595.276, 841.89]).drawText('Alice');
    return Buffer.from(await pdf.save());
  });
  const r = await run(f.html, { autoHeal: true, outputPdf: f.pdf });
  assert.equal(r.status, 'FAIL');
  assert.ok(r.checks.auto_heal.iterations > 0);
  assert.deepEqual(await fs.readFile(f.html), before);
  assert.equal(await fs.readFile(f.pdf, 'utf8'), 'OLD');
});
test('PDF crop clipping fails even when MediaBox is A4', async t => {
  const f = await fixture(t);
  await patchPdf(t, async bytes => {
    const pdf = await PDFDocument.load(bytes); pdf.getPage(0).setCropBox(0, 0, 100, 100);
    return Buffer.from(await pdf.save());
  });
  const r = await run(f.html);
  assert.equal(r.checks.pdf.status, 'FAIL');
});
for (const [label, body] of [
  ['empty name', page('')],
  ['missing name', page('Alice').replace('candidate-name', 'other')],
  ['hidden name', page('Alice').replace('class="candidate-name"', 'class="candidate-name" style="display:none"')],
  ['hidden name text', page('<span style="display:none">Alice</span>')],
  ['duplicate name', page('Alice') + '<h1 class="candidate-name">Other</h1>'],
  ['no substance', '<article class="resume-page"><h1 class="candidate-name">Alice</h1></article>']
]) test(`reject canvas with ${label}`, async t => {
  const f = await fixture(t, body);
  assert.equal((await run(f.html)).status, 'FAIL');
});
test('two pages exceed limit one', async t => {
  const f = await fixture(t, page('Alice') + page('Bob'));
  const r = await run(f.html, { expectedPages: 1 });
  assert.equal(r.status, 'FAIL');
  assert.equal(r.checks.pdf.status, 'FAIL');
});
test('single root natural multipage flow is explicitly rejected', async t => {
  const f = await fixture(t, page('Alice'), '.resume-page{height:600mm}');
  const r = await run(f.html, { expectedPages: 2 });
  assert.equal(r.status, 'FAIL');
  assert.ok(r.errors.some(e => e.includes('explicit .resume-page')));
});
test('Chinese wrapped text fragments survive normalization', async t => {
  const f = await fixture(t, page('张明') + '', 'p{width:100px}');
  let html = await fs.readFile(f.html, 'utf8');
  html = html.replace('Education University 2020 2024', '教育经历北京大学计算机科学专业毕业时间二零二四年研究分布式系统与数据库');
  await fs.writeFile(f.html, html);
  pass(await run(f.html, { expectedPages: 2 }));
});
test('system browser fallback is detected without environment override', async t => {
  const f = await fixture(t);
  const launch = playwright.chromium.launch;
  const paths = [];
  playwright.chromium.launch = async function (options) {
    paths.push(options.executablePath);
    if (!options.executablePath) throw new Error('bundled unavailable');
    // Exercise selection without requiring every host to have system Chrome.
    return launch.call(this, { headless: true });
  };
  t.after(() => { playwright.chromium.launch = launch; });
  const bin = path.join(f.dir, 'chromium');
  await fs.writeFile(bin, '', { mode: 0o755 });
  const oldPath = process.env.PATH;
  process.env.PATH = f.dir + path.delimiter + oldPath;
  t.after(() => { process.env.PATH = oldPath; });
  pass(await run(f.html));
  assert.equal(paths[0], undefined);
  assert.ok(paths[1]);
});
for (const rule of ['display:none', 'opacity:0', 'visibility:hidden']) test(`hidden education fails: ${rule}`, async t => {
  const f = await fixture(t, page('Alice').replace('</article>', '<div class="education">Education hidden degree 2021</div></article>'), `@media print{.education{${rule}}}`);
  const r = await run(f.html, { outputPdf: f.pdf });
  assert.equal(r.status, 'FAIL');
  assert.ok(r.checks.dom.issues.some(i => i.reason.includes('Hidden')));
});
test('output hashes bind exact published bytes including healed HTML', async t => {
  const { createHash } = require('node:crypto');
  const f = await fixture(t, healBody, healCSS);
  const r = await run(f.html, { outputPdf: f.pdf, autoHeal: true });
  pass(r);
  for (const [file, key] of [[f.html, 'htmlSha256'], [f.pdf, 'pdfSha256']])
    assert.equal(r.checks.output[key], createHash('sha256').update(await fs.readFile(file)).digest('hex'));
});
test('output write failure exits FAIL=1', async t => {
  const f = await fixture(t);
  const p = spawnSync('node', ['scripts/rendering/browser-engine.js', f.html, '--output', f.html + '/resume.pdf'], { encoding: 'utf8' });
  assert.equal(p.status, 1, p.stderr);
  const r = JSON.parse(p.stdout);
  assert.equal(r.status, 'FAIL');
  assert.equal(r.checks.output.status, 'FAIL');
});

test('literal template syntax is valid user text', async t => {
  const f = await fixture(t, page('Alice').replace('Education University', 'Built {{template}} editor at University'));
  pass(await run(f.html));
});
test('unbound resume slot comments fail closed', async t => {
  const f = await fixture(t, page('Alice').replace('</article>', '<!-- resume:education --></article>'));
  const r = await run(f.html);
  assert.equal(r.status, 'FAIL');
});

test('an unavailable explicit local font cannot silently fall back and pass', async t => {
  const f = await fixture(t, page('Alice'), '@font-face{font-family:KnowMeMissing;src:local("KnowMe intentionally absent font 6f90b4")} .resume-page{font-family:KnowMeMissing,Arial}');
  const r = await run(f.html);
  assert.equal(r.status, 'UNVERIFIED');
  assert.equal(r.checks.fonts.status, 'UNVERIFIED');
});
