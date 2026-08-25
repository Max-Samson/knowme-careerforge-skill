/**
 * KnowMe CareerForge CLI — List Command
 * 列出本地知识库中所有可用岗位技能画像、核心模板与布局样式。
 */

import * as fs from 'fs';
import * as path from 'path';

function getRootDir(): string {
  let curr = __dirname;
  for (let i = 0; i < 6; i++) {
    if (fs.existsSync(path.join(curr, 'src', 'templates')) && fs.existsSync(path.join(curr, 'SKILL.md'))) {
      return curr;
    }
    curr = path.dirname(curr);
  }
  return path.resolve(__dirname, '../../..');
}

export function runList(): void {
  const rootDir = getRootDir();
  const rolesDir = path.join(rootDir, 'src', 'knowledge', 'roles');
  const templatesDir = path.join(rootDir, 'src', 'templates');

  console.log('==============================================================');
  console.log('  KnowMe CareerForge — Available Roles & Templates Inventory');
  console.log(`  Package Root: ${rootDir}`);
  console.log('==============================================================');

  // 1. 列出岗位画像
  console.log('\n[1. Structured Role Knowledge Profiles]:');
  if (fs.existsSync(rolesDir)) {
    const roleFiles = fs.readdirSync(rolesDir).filter(f => f.endsWith('.json'));
    for (const rf of roleFiles) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(rolesDir, rf), 'utf-8'));
        console.log(`  • [${data.id}] ${data.name} (${data.category})`);
        console.log(`    Must-have: ${(data.mustHaveSkills || []).slice(0, 4).join(', ')}`);
      } catch {}
    }
  }

  // 2. 列出核心模板
  console.log('\n[2. Core HTML Resume Templates]:');
  if (fs.existsSync(templatesDir)) {
    const tDirs = fs.readdirSync(templatesDir).filter(d => d !== 'common');
    for (const td of tDirs) {
      const metaPath = path.join(templatesDir, td, 'metadata.json');
      if (fs.existsSync(metaPath)) {
        try {
          const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
          console.log(`  • [${meta.id}] ${meta.name} (Style: ${meta.style})`);
          console.log(`    Target: ${meta.layout?.targetPages} page(s) | ATS: ${meta.atsScoreTier} | Tone: ${meta.visualStyle?.tone}`);
          console.log(`    Tokens: ${(meta.customizableTokens || []).slice(0, 3).join(', ')}`);
        } catch {}
      }
    }
  }

  console.log('\n==============================================================');
}
