#!/usr/bin/env node
'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { randomUUID, createHash } = require('node:crypto');

const CHECKS = ['input', 'fonts', 'dom', 'pdf', 'text', 'output'];
function resultFor(html, expectedPages) {
  return { status: 'UNVERIFIED', file: path.resolve(html), expectedPages,
    errors: [], warnings: [], checks: Object.fromEntries(CHECKS.map(k => [k, { status: 'UNVERIFIED' }])) };
}
function failure(result, check, message, status = 'FAIL') {
  result.checks[check] = { ...result.checks[check], status };
  result.errors.push(`${check}: ${message}`);
}
function finish(result) {
  result.status = result.errors.length
    ? (Object.values(result.checks).some(c => c.status === 'FAIL') ? 'FAIL' : 'UNVERIFIED')
    : Object.values(result.checks).every(c => c.status === 'PASS') ? 'PASS' : 'UNVERIFIED';
  return result;
}

// Executed in the print-media page. Never relax height/overflow constraints.
function inspectDOM() {
  const tolerance = 0.75;
  const pages = [...document.querySelectorAll('.resume-page')];
  const issues = [];
  const unsupported = [];
  const rect = r => ({ left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height });
  const label = e => e.id ? `#${e.id}` : e.tagName.toLowerCase() + (e.classList.length ? '.' + [...e.classList].join('.') : '');
  function visible(e) {
    for (let a = e; a; a = a.parentElement) {
      const s = getComputedStyle(a);
      if (s.display === 'none' || Number(s.opacity) === 0) return false;
    }
    return getComputedStyle(e).visibility === 'visible';
  }
  const details = pages.map((p, i) => {
    const bounds = p.getBoundingClientRect();
    const pageIndex = i + 1;
    if (!visible(p) || !bounds.width || !bounds.height) issues.push({ pageIndex, selector: label(p), reason: 'invisible/empty page' });
    if (bounds.width > 210 * 96 / 25.4 + tolerance || bounds.height > 297 * 96 / 25.4 + tolerance)
      issues.push({ pageIndex, selector: label(p), reason: 'page exceeds A4', bounds: rect(bounds) });
    function check(r, e, isPage = false) {
      const sides = [];
      if (r.left < bounds.left - tolerance) sides.push('left');
      if (r.top < bounds.top - tolerance) sides.push('top');
      if (r.right > bounds.right + tolerance) sides.push('right');
      if (r.bottom > bounds.bottom + tolerance) sides.push('bottom');
      if (sides.length) issues.push({ pageIndex, selector: label(e), reason: 'page boundary', sides, bounds: rect(r) });
      for (let a = isPage ? e.parentElement : e; a; a = a.parentElement) {
        const s = getComputedStyle(a);
        const b = a.getBoundingClientRect();
        const left = b.left + a.clientLeft, top = b.top + a.clientTop;
        const clipX = /hidden|clip|scroll|auto/.test(s.overflowX);
        const clipY = /hidden|clip|scroll|auto/.test(s.overflowY);
        const paint = /paint|strict|content/.test(s.contain);
        if (((clipX || paint) && (r.left < left - tolerance || r.right > left + a.clientWidth + tolerance)) ||
            ((clipY || paint) && (r.top < top - tolerance || r.bottom > top + a.clientHeight + tolerance)))
          issues.push({ pageIndex, selector: label(e), ancestor: label(a), reason: 'ancestor clipping', bounds: rect(r) });
        if (s.clipPath !== 'none' || (s.maskImage && s.maskImage !== 'none') || s.clip !== 'auto')
          unsupported.push({ pageIndex, selector: label(a), reason: 'non-rectangular/legacy clipping requires visual verification' });
      }
    }
    check(bounds, p, true);
    const text = [];
    for (const e of [p, ...p.querySelectorAll('*')]) {
      if (/^(SCRIPT|STYLE|TEMPLATE|NOSCRIPT)$/.test(e.tagName)) continue;
      if (!visible(e)) {
        if ([...e.childNodes].some(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim()))
          issues.push({ pageIndex, selector: label(e), reason: 'Hidden nonempty body text in print media' });
        continue;
      }
      if (e !== p) for (const r of e.getClientRects()) check(r, e.parentElement);
      for (const node of e.childNodes) {
        if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const rs = [...range.getClientRects()];
        if (!rs.length) continue;
        text.push(node.textContent);
        for (const r of rs) check(r, e);
      }
    }
    return { pageIndex, bounds: rect(bounds), text: text.join(' '), textFragments: text };
  });
  const names = [...document.querySelectorAll('h1.candidate-name')];
  const validName = names.length === 1 && visible(names[0]) && names[0].getBoundingClientRect().width > 0 && names[0].getBoundingClientRect().height > 0 && !!names[0].innerText.replace(/[\s\u200b-\u200f\ufeff]/g, '') && !!names[0].closest('.resume-page');
  if (!validName) issues.push({ reason: 'Require exactly one nonempty visible h1.candidate-name inside a resume page' });
  const compact = text => text.replace(/\s/g, '');
  const substantive = compact(details.map(p => p.text).join('')).replace(validName ? compact(names[0].innerText) : '', '');
  if (substantive.length < 20) issues.push({ reason: 'Require at least 20 non-whitespace body characters beyond the name' });
  const comments = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT);
  while (comments.nextNode()) {
    if (/^\s*resume:/.test(comments.currentNode.data))
      issues.push({ reason: 'Unbound canvas slot remains in the document' });
  }
  if (/\{\{\s*resume:language\s*\}\}/.test(document.documentElement.lang))
    issues.push({ reason: 'Unbound canvas language slot' });
  return { totalPagesFound: pages.length, pages: details, issues, unsupported, candidateName: validName ? names[0].innerText.trim() : null, bodyCharacters: substantive.length };
}

function normalized(text) {
  return text.normalize('NFKC').replace(/[\s\u200b-\u200f\u202a-\u202e\u2060\ufeff\u00ad]/gu, '');
}
// Compare character multiplicities, tolerating PDF column/RTL extraction order only.
function missingText(expected, actual) {
  const counts = new Map();
  for (const c of normalized(actual)) counts.set(c, (counts.get(c) || 0) + 1);
  let missing = '';
  for (const c of normalized(expected)) {
    if ((counts.get(c) || 0) > 0) counts.set(c, counts.get(c) - 1);
    else missing += c;
  }
  return missing;
}

const ladder = [
  ...[10.5, 9.5, 8.5].map(n => ({ '--resume-space-section': `${n}pt` })),
  ...[[7, 2.5], [6, 2], [5, 1.5]].map(([a, b]) => ({ '--resume-space-item': `${a}pt`, '--resume-space-bullet': `${b}pt` })),
  ...[[9, 1.42], [8.8, 1.38]].map(([a, b]) => ({ '--resume-font-size-body': `${a}pt`, '--resume-line-height-body': `${b}` }))
];
// Only edit existing numeric root declarations, never insert or increase a token.
function reduceTokens(html, targets) {
  const tuned = {};
  const content = html.replace(/(<style\b[^>]*>)([\s\S]*?)(<\/style>)/gi, (all, open, css, close) =>
    open + css.replace(/(:root\s*\{)([^}]*)(\})/g, (block, start, body, end) => {
      for (const [token, value] of Object.entries(targets)) {
        const target = /^([\d.]+)(pt)?$/.exec(value);
        body = body.replace(new RegExp(`(${token}\\s*:\\s*)([\\d.]+)(pt)?(\\s*;)`, 'g'), (decl, prefix, n, unit, semi) => {
          if ((unit || '') !== (target[2] || '') || Number(n) <= Number(target[1])) return decl;
          tuned[token] = value;
          return prefix + value + semi;
        });
      }
      return start + body + end;
    }) + close);
  return { content, tuned };
}

async function dependencies() {
  let pw;
  try { pw = require('playwright'); } catch { pw = require('playwright-core'); }
  const { PDFDocument } = require('pdf-lib');
  const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
  return { pw, PDFDocument, pdfjs };
}

async function systemBrowsers() {
  const home = require('node:os').homedir();
  const candidates = [
    ...['/Applications', path.join(home, 'Applications')].flatMap(base => [
      'Google Chrome.app/Contents/MacOS/Google Chrome', 'Chromium.app/Contents/MacOS/Chromium',
      'Microsoft Edge.app/Contents/MacOS/Microsoft Edge', 'Brave Browser.app/Contents/MacOS/Brave Browser'
    ].map(name => path.join(base, name))),
    ...[process.env.PROGRAMFILES, process.env['PROGRAMFILES(X86)'], process.env.LOCALAPPDATA].filter(Boolean).flatMap(base => [
      'Google/Chrome/Application/chrome.exe', 'Microsoft/Edge/Application/msedge.exe', 'BraveSoftware/Brave-Browser/Application/brave.exe'
    ].map(name => path.join(base, name))),
    ...(process.env.PATH || '').split(path.delimiter).filter(Boolean).flatMap(base =>
      ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'brave-browser'].map(name => path.join(base, name)))
  ];
  const found = [];
  for (const candidate of new Set(candidates)) {
    try { await fs.access(candidate, require('node:fs').constants.X_OK); found.push(candidate); } catch {}
  }
  return found;
}
async function launchBrowser(pw) {
  const override = process.env.CHROME_BIN || process.env.BROWSER_PATH;
  if (override) return pw.chromium.launch({ headless: true, executablePath: override });
  const failures = [];
  for (const executablePath of [undefined, ...await systemBrowsers()]) {
    try { return await pw.chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) }); }
    catch (error) { failures.push(`${executablePath || 'bundled Chromium'}: ${error.message}`); }
  }
  throw new Error(`No usable browser: ${failures.join('\n')}`);
}

async function inspect(page, htmlFile, expectedPages, deps) {
  const result = resultFor(htmlFile, expectedPages);
  result.checks.input = { status: 'PASS' };
  let phase = 'fonts';
  const resourceErrors = [];
  const onFailed = request => resourceErrors.push(request.url());
  const onResponse = response => { if (response.status() >= 400) resourceErrors.push(response.url()); };
  page.on('requestfailed', onFailed);
  page.on('response', onResponse);
  try {
    await page.emulateMedia({ media: 'print' });
    await page.goto(pathToFileURL(htmlFile).href, { waitUntil: 'networkidle', timeout: 30000 });
    await page.evaluate(async () => {
      await Promise.race([document.fonts.ready, new Promise((_, reject) => setTimeout(() => reject(new Error('Font wait timed out')), 15000))]);
      if ([...document.fonts].some(f => f.status === 'error')) throw new Error('A font failed to load');
      await Promise.all([...document.images].map(img => img.decode()));
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    });
    if (resourceErrors.length) throw new Error(`Resources failed to load: ${resourceErrors.join(', ')}`);
    result.checks.fonts = { status: 'PASS' };
    phase = 'dom';
    const dom = await page.evaluate(inspectDOM);
    result.checks.dom = { status: 'PASS', ...dom };
    if (dom.totalPagesFound < 1 || dom.totalPagesFound > expectedPages) failure(result, 'dom', `Require 1–${expectedPages} explicit .resume-page containers, found ${dom.totalPagesFound}`);
    if (dom.issues.length) failure(result, 'dom', `${dom.issues.length} boundary/clipping violations`);
    if (dom.unsupported.length && !dom.issues.length) failure(result, 'dom', 'Unsupported clipping', 'UNVERIFIED');
    phase = 'pdf';
    const bytes = await page.pdf({ format: 'A4', preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: false, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    const pdf = await deps.PDFDocument.load(bytes);
    const sizes = pdf.getPages().map((p, i) => ({ pageIndex: i + 1, ...p.getSize(), cropBox: p.getCropBox(), rotation: p.getRotation().angle }));
    result.checks.pdf = { status: 'PASS', pageCount: sizes.length, pages: sizes };
    if (sizes.length < 1 || sizes.length > expectedPages) failure(result, 'pdf', `Page limit ${expectedPages}, generated ${sizes.length}`);
    if (sizes.length !== dom.totalPagesFound) failure(result, 'pdf', 'Each physical PDF page must have its own explicit .resume-page container; flowing one container over multiple pages is unsupported');
    if (sizes.some(p => Math.abs(p.width - 595.276) > 1 || Math.abs(p.height - 841.89) > 1 || p.rotation % 360 !== 0 || Math.abs(p.cropBox.x) > 1 || Math.abs(p.cropBox.y) > 1 || Math.abs(p.cropBox.width - p.width) > 1 || Math.abs(p.cropBox.height - p.height) > 1))
      failure(result, 'pdf', 'Every PDF page must be portrait A4 (1pt tolerance)');
    phase = 'text';
    const task = deps.pdfjs.getDocument({ data: new Uint8Array(bytes), useSystemFonts: true, verbosity: 0 });
    try {
      const doc = await task.promise;
      const pages = [];
      for (let n = 1; n <= doc.numPages; n++) {
        const content = await (await doc.getPage(n)).getTextContent();
        const text = content.items.map(item => item.str || '').join(' ');
        const expected = dom.pages[n - 1]?.text || '';
        const missing = missingText(expected, text);
        const missingFragments = (dom.pages[n - 1]?.textFragments || [])
          .map(normalized).filter(fragment => fragment && !normalized(text).includes(fragment));
        const codepoints = value => [...new Set([...value])].map(character => ({
          character, codepoint: 'U+' + character.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')
        }));
        const extractedRadicals = [...text].filter(character => {
          const cp = character.codePointAt(0); return cp >= 0x2E80 && cp <= 0x2FDF;
        }).join('');
        pages.push({ pageIndex: n, text, expectedCharacters: normalized(expected).length, missing, missingFragments,
          missingCodepoints: codepoints(missing), extractedRadicals: codepoints(extractedRadicals) });
        if (missing && extractedRadicals)
          result.warnings.push(`Page ${n}: extracted radical codepoints may indicate font mapping differences. Inspect missingCodepoints/extractedRadicals; choose an available explicit font and rerun without changing the facts.`);
      }
      result.checks.text = { status: 'PASS', pages };
      if (doc.numPages !== sizes.length || pages.some(p => !normalized(p.text) || !p.expectedCharacters || p.missing || p.missingFragments.length || p.text.includes('\ufffd')))
        failure(result, 'text', 'Blank, missing, undecodable or mismatched per-page PDF text');
    } finally { await task.destroy(); }
    result.checks.output = { status: 'PASS', committed: false };
    return { result: finish(result), bytes };
  } catch (error) {
    failure(result, phase, error.message, 'UNVERIFIED');
    return { result: finish(result) };
  } finally {
    page.off('requestfailed', onFailed);
    page.off('response', onResponse);
  }
}

async function run(html, { expectedPages = 1, autoHeal = false, outputPdf } = {}) {
  const initial = resultFor(html, expectedPages);
  const source = initial.file;
  let browser, stagedHtml, stagedPdf, backupHtml;
  let phase = 'input';
  try {
    if (![1, 2].includes(expectedPages)) {
      failure(initial, 'input', 'expectedPages must be the page limit 1 or 2'); return finish(initial);
    }
    const originalBytes = await fs.readFile(source);
    const original = originalBytes.toString('utf8');
    const output = outputPdf ? path.resolve(outputPdf) : null;
    if (output && (output === source || await fs.realpath(output).catch(() => output) === await fs.realpath(source))) {
      failure(initial, 'input', 'PDF output must differ from HTML source'); return finish(initial);
    }
    initial.checks.input = { status: 'PASS' };
    phase = 'fonts';
    const deps = await dependencies();
    browser = await launchBrowser(deps.pw);
    const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
    let attempt = await inspect(page, source, expectedPages, deps);
    let candidate = original;
    const tunedTokens = {};
    let iterations = 0;
    if (autoHeal && attempt.result.status === 'FAIL' && attempt.result.checks.dom.issues?.length) {
      stagedHtml = path.join(path.dirname(source), `.${path.basename(source)}.${randomUUID()}.html`);
      for (const targets of ladder) {
        const reduced = reduceTokens(candidate, targets);
        if (reduced.content === candidate) continue;
        candidate = reduced.content;
        Object.assign(tunedTokens, reduced.tuned);
        await fs.writeFile(stagedHtml, candidate, { mode: (await fs.stat(source)).mode });
        iterations++;
        attempt = await inspect(page, stagedHtml, expectedPages, deps);
        if (attempt.result.status !== 'FAIL') break;
      }
    }
    await browser.close(); browser = null;
    const result = attempt.result;
    result.file = source;
    result.checks.auto_heal = { status: result.status, requested: autoHeal, healed: result.status === 'PASS', iterations,
      tunedTokens: result.status === 'PASS' ? tunedTokens : {}, committed: false };
    if (result.status !== 'PASS') return result;
    phase = 'output';
    // All validation and browser shutdown precede publication. Each file is replaced
    // by a same-directory rename; roll back HTML if the PDF rename fails.
    try {
      if (!(await fs.readFile(source)).equals(originalBytes)) throw new Error('HTML changed during validation');
      if (output) {
        await fs.mkdir(path.dirname(output), { recursive: true });
        stagedPdf = path.join(path.dirname(output), `.${path.basename(output)}.${randomUUID()}.tmp`);
        await fs.writeFile(stagedPdf, attempt.bytes, { flag: 'wx' });
      }
      if (iterations) {
        backupHtml = path.join(path.dirname(source), `.${path.basename(source)}.${randomUUID()}.backup`);
        await fs.copyFile(source, backupHtml);
      }
      let htmlCommitted = false;
      try {
        if (iterations) { await fs.rename(stagedHtml, source); htmlCommitted = true; }
        if (output) await fs.rename(stagedPdf, output);
      } catch (error) {
        if (htmlCommitted) {
          await fs.rename(backupHtml, source);
        }
        throw error;
      }
      result.checks.auto_heal.committed = iterations > 0;
      result.checks.output = { status: 'PASS', committed: !!output, path: output,
        pdfSha256: createHash('sha256').update(attempt.bytes).digest('hex'),
        htmlSha256: createHash('sha256').update(iterations ? Buffer.from(candidate, 'utf8') : originalBytes).digest('hex') };
      return finish(result);
    } catch (error) { failure(result, 'output', error.message, 'FAIL'); return finish(result); }
  } catch (error) {
    failure(initial, phase, error.message, error.code === 'ENOENT' && phase === 'input' ? 'FAIL' : 'UNVERIFIED');
    return finish(initial);
  } finally {
    if (browser) await browser.close().catch(() => {});
    for (const file of [stagedHtml, stagedPdf, backupHtml]) if (file) await fs.unlink(file).catch(() => {});
  }
}

async function cli(args = process.argv.slice(2), defaults = {}) {
  let html = 'workspace/resume.html';
  const options = { ...defaults };
  const positional = [];
  let bad;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (['--html', '--input', '-i'].includes(arg)) html = args[++i];
    else if (['--output', '-o', '--output-pdf'].includes(arg)) {
      options.outputPdf = args[++i];
      if (!options.outputPdf || options.outputPdf.startsWith('-')) bad = 'Missing PDF output path';
    }
    else if (['--expected-pages', '-p'].includes(arg)) options.expectedPages = Number(args[++i]);
    else if (arg === '--auto-heal') options.autoHeal = true;
    else if (['--json', '--quiet', '-q'].includes(arg)) continue;
    else if (arg.startsWith('-')) bad = `Unknown argument: ${arg}`;
    else positional.push(arg);
  }
  if (positional.length > 2) bad = 'Too many positional arguments';
  html = positional[0] || html;
  if (positional[1]) options.outputPdf = positional[1];
  let result;
  if (bad || !html) { result = resultFor(html || '.', options.expectedPages || 1); failure(result, 'input', bad || 'Missing HTML path'); finish(result); }
  else result = await run(html, options);
  process.stdout.write(JSON.stringify(result) + '\n');
  process.exitCode = result.status === 'PASS' ? 0 : result.status === 'FAIL' ? 1 : 2;
  return result;
}
module.exports = { run, cli, reduceTokens, missingText, systemBrowsers };
if (require.main === module) cli();
