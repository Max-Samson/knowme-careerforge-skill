#!/usr/bin/env ts-node
/**
 * KnowMe CareerForge — ATS Text Flow & Heading Hierarchy Inspector
 * 验证 HTML 简历中的关键文本可提取性、标头层级规范与 ATS 机器解析友好度。
 */

import { chromium } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

interface AtsValidationResult {
  status: 'PASS' | 'WARN' | 'FAIL';
  candidateName: string | null;
  detectedContacts: {
    phone: string | null;
    email: string | null;
  };
  headingsFound: Array<{
    level: string;
    text: string;
    isStandard: boolean;
  }>;
  totalTextLength: number;
  warnings: string[];
  errors: string[];
}

const STANDARD_SECTION_HEADERS = [
  '工作经历', '工作经验', 'work experience', 'experience',
  '项目经历', '核心项目', 'projects', 'key projects',
  '专业技能', '核心技能', 'skills', 'technical skills',
  '教育背景', '教育经历', 'education',
  '核心领导力', '重大经历', '资质与证书', '求职意向'
];

export async function validateAts(htmlPath: string): Promise<AtsValidationResult> {
  const absoluteHtml = path.resolve(htmlPath);
  if (!fs.existsSync(absoluteHtml)) {
    throw new Error(`HTML file not found: ${absoluteHtml}`);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(`file://${absoluteHtml}`, { waitUntil: 'networkidle' });

  const rawData = await page.evaluate(() => {
    const nameEl = document.querySelector('.candidate-name, h1');
    const name = nameEl ? (nameEl.textContent || '').trim() : null;

    const fullText = (document.body.innerText || '').trim();

    // 提取电话与邮箱
    const phoneMatch = fullText.match(/(?:(?:\+|00)86)?1[3-9]\d{9}|(?:1[3-9]\d-\d{4}-\d{4})/);
    const emailMatch = fullText.match(/[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/);

    const headings = Array.from(document.querySelectorAll('h1, h2, h3, .section-title, .sub-title')).map(h => ({
      level: h.tagName.toLowerCase(),
      text: (h.textContent || '').trim()
    }));

    return {
      candidateName: name,
      phone: phoneMatch ? phoneMatch[0] : null,
      email: emailMatch ? emailMatch[0] : null,
      headings,
      fullTextLength: fullText.length
    };
  });

  await browser.close();

  const warnings: string[] = [];
  const errors: string[] = [];

  if (!rawData.candidateName) {
    errors.push('Candidate name (.candidate-name or h1) could not be extracted');
  }

  if (!rawData.email) {
    warnings.push('No valid email address pattern detected in text flow');
  }

  if (!rawData.phone) {
    warnings.push('No standard mobile phone pattern detected in text flow');
  }

  const validatedHeadings = rawData.headings.map(h => {
    const textClean = h.text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '');
    const isStd = STANDARD_SECTION_HEADERS.some(s => textClean.includes(s.toLowerCase().replace(/\s+/g, '')));
    return {
      level: h.level,
      text: h.text,
      isStandard: isStd
    };
  });

  const nonStdHeadings = validatedHeadings.filter(h => !h.isStandard && h.level === 'h2');
  if (nonStdHeadings.length > 0) {
    warnings.push(`Non-standard section headings detected: ${nonStdHeadings.map(h => `"${h.text}"`).join(', ')}`);
  }

  const status: 'PASS' | 'WARN' | 'FAIL' = errors.length > 0 ? 'FAIL' : warnings.length > 0 ? 'WARN' : 'PASS';

  return {
    status,
    candidateName: rawData.candidateName,
    detectedContacts: {
      phone: rawData.phone,
      email: rawData.email
    },
    headingsFound: validatedHeadings,
    totalTextLength: rawData.fullTextLength,
    warnings,
    errors
  };
}

async function main() {
  const args = process.argv.slice(2);
  let htmlPath = 'workspace/resume.html';
  let jsonOutput = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--html' || args[i] === '-i') {
      htmlPath = args[i + 1];
      i++;
    } else if (args[i] === '--json') {
      jsonOutput = true;
    }
  }

  try {
    const result = await validateAts(htmlPath);

    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log('======================================================');
    console.log(`  KnowMe CareerForge — ATS Compliance QA: [${result.status}]`);
    console.log(`  Candidate Name : ${result.candidateName || 'N/A'}`);
    console.log(`  Phone Extracted: ${result.detectedContacts.phone || 'None'}`);
    console.log(`  Email Extracted: ${result.detectedContacts.email || 'None'}`);
    console.log(`  Text Extracted : ${result.totalTextLength} characters`);
    console.log('------------------------------------------------------');
    console.log('  Headings Structure:');
    for (const h of result.headingsFound) {
      const tag = h.isStandard ? '✓' : '?';
      console.log(`    [${tag}] <${h.level}> ${h.text}`);
    }

    if (result.errors.length > 0) {
      console.log('\n[!] Errors:');
      for (const e of result.errors) console.log(`  - ✗ ${e}`);
    }

    if (result.warnings.length > 0) {
      console.log('\n[?] Warnings:');
      for (const w of result.warnings) console.log(`  - ⚠️ ${w}`);
    }

    console.log('======================================================');
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[✗] ATS Validation Failed: ${msg}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
