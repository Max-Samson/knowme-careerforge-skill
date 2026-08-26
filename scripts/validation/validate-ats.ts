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
    email: string | null;
    phone: string | null;
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
    const nameEl = document.querySelector('.candidate-name') || document.querySelector('h1');
    const candidateName = nameEl ? nameEl.textContent?.trim() || null : null;

    const bodyText = document.body.innerText || '';
    const emailMatch = bodyText.match(/[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/);
    const phoneMatch = bodyText.match(/1[3-9]\d{9}|\+?\d{1,4}[-\s]?\d{7,11}/);

    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4')).map(h => ({
      level: h.tagName.toLowerCase(),
      text: h.textContent?.replace(/[\s\n]+/g, ' ').trim() || ''
    }));

    return {
      candidateName,
      email: emailMatch ? emailMatch[0] : null,
      phone: phoneMatch ? phoneMatch[0] : null,
      headings,
      totalTextLength: bodyText.trim().length
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
    const textClean = h.text.toLowerCase();
    const isStandard = STANDARD_SECTION_HEADERS.some(sh => textClean.includes(sh.toLowerCase()));
    return {
      ...h,
      isStandard
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
      email: rawData.email,
      phone: rawData.phone
    },
    headingsFound: validatedHeadings,
    totalTextLength: rawData.totalTextLength,
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
    } else if (!args[i].startsWith('-')) {
      htmlPath = args[i];
    }
  }

  try {
    const result = await validateAts(htmlPath);

    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
      process.exit(result.status === 'FAIL' ? 1 : 0);
    }

    console.log('======================================================');
    console.log(`  KnowMe CareerForge — ATS Compliance QA: [${result.status}]`);
    console.log(`  Candidate Name : ${result.candidateName || 'NOT FOUND'}`);
    console.log(`  Phone Extracted: ${result.detectedContacts.phone || 'NOT DETECTED'}`);
    console.log(`  Email Extracted: ${result.detectedContacts.email || 'NOT DETECTED'}`);
    console.log(`  Text Extracted : ${result.totalTextLength} characters`);
    console.log('------------------------------------------------------');
    console.log('  Headings Structure:');
    for (const h of result.headingsFound) {
      const mark = h.isStandard ? '[✓]' : '[?]';
      console.log(`    ${mark} <${h.level}> ${h.text}`);
    }

    if (result.warnings.length > 0) {
      console.log('\n[!] Warnings:');
      for (const w of result.warnings) {
        console.log(`  - ⚠️  ${w}`);
      }
    }

    if (result.errors.length > 0) {
      console.log('\n[✗] Errors:');
      for (const e of result.errors) {
        console.log(`  - ✗ ${e}`);
      }
    }

    console.log('======================================================');
    process.exit(result.status === 'FAIL' ? 1 : 0);
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[✗] ATS Validation Failed: ${errorMsg}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
