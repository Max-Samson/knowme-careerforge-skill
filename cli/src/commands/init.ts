/**
 * KnowMe CareerForge CLI — Init Command
 * 一键将 Skill 注入并配置至指定 AI Agent 平台环境。
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface InitOptions {
  platform?: string;
  all?: boolean;
  projectDir?: string;
}

const SUPPORTED_PLATFORMS = ['claude', 'codex', 'cursor', 'windsurf', 'gemini', 'opencode'];

function findPackageRoot(startDir: string): string {
  let curr = startDir;
  for (let i = 0; i < 6; i++) {
    if (fs.existsSync(path.join(curr, 'src', 'templates')) && fs.existsSync(path.join(curr, 'SKILL.md'))) {
      return curr;
    }
    curr = path.dirname(curr);
  }
  return path.resolve(startDir, '../../..');
}

export function runInit(options: InitOptions): void {
  const rootDir = findPackageRoot(__dirname);
  const projectDir = options.projectDir ? path.resolve(options.projectDir) : process.cwd();
  const homeDir = os.homedir();

  const targetPlatforms = options.all
    ? SUPPORTED_PLATFORMS
    : options.platform
      ? [options.platform.toLowerCase()]
      : ['cursor'];

  console.log('==============================================================');
  console.log('  KnowMe CareerForge CLI — Skill Initializer');
  console.log(`  Source Skill  : ${rootDir}`);
  console.log(`  Target Project: ${projectDir}`);
  console.log(`  Platforms     : ${targetPlatforms.join(', ')}`);
  console.log('==============================================================');

  for (const plat of targetPlatforms) {
    try {
      switch (plat) {
        case 'claude': {
          const claudeDir = path.join(homeDir, '.claude', 'skills', 'knowme-careerforge');
          fs.mkdirSync(claudeDir, { recursive: true });
          const skillMd = fs.readFileSync(path.join(rootDir, 'SKILL.md'), 'utf-8');
          fs.writeFileSync(path.join(claudeDir, 'SKILL.md'), skillMd, 'utf-8');
          console.log(`[✓] Claude Code Skill configured -> ${claudeDir}`);
          break;
        }
        case 'codex': {
          const codexDir = path.join(homeDir, '.codex', 'skills', 'knowme-careerforge');
          fs.mkdirSync(codexDir, { recursive: true });
          const skillMd = fs.readFileSync(path.join(rootDir, 'SKILL.md'), 'utf-8');
          fs.writeFileSync(path.join(codexDir, 'SKILL.md'), skillMd, 'utf-8');
          console.log(`[✓] Codex Native Skill configured -> ${codexDir}`);
          break;
        }
        case 'cursor': {
          const cursorRulesDir = path.join(projectDir, '.cursor', 'rules');
          fs.mkdirSync(cursorRulesDir, { recursive: true });
          const mdcContent = fs.readFileSync(path.join(rootDir, 'agents', 'cursor', 'knowme-careerforge.mdc'), 'utf-8');
          fs.writeFileSync(path.join(cursorRulesDir, 'knowme-careerforge.mdc'), mdcContent, 'utf-8');
          console.log(`[✓] Cursor MDC Rule configured -> ${path.join(cursorRulesDir, 'knowme-careerforge.mdc')}`);
          break;
        }
        case 'windsurf': {
          const windsurfRulePath = path.join(projectDir, '.windsurfrules');
          const ruleContent = fs.readFileSync(path.join(rootDir, 'agents', 'windsurf', 'knowme-careerforge.rules'), 'utf-8');
          fs.appendFileSync(windsurfRulePath, `\n\n${ruleContent}`, 'utf-8');
          console.log(`[✓] Windsurf Rule configured -> ${windsurfRulePath}`);
          break;
        }
        case 'gemini': {
          const geminiDir = path.join(homeDir, '.gemini', 'skills');
          fs.mkdirSync(geminiDir, { recursive: true });
          const geminiJson = fs.readFileSync(path.join(rootDir, 'agents', 'gemini', 'knowme-careerforge.json'), 'utf-8');
          fs.writeFileSync(path.join(geminiDir, 'knowme-careerforge.json'), geminiJson, 'utf-8');
          console.log(`[✓] Gemini CLI Skill configured -> ${path.join(geminiDir, 'knowme-careerforge.json')}`);
          break;
        }
        case 'opencode': {
          const opencodeDir = path.join(projectDir, '.opencode', 'skills', 'knowme-careerforge');
          fs.mkdirSync(opencodeDir, { recursive: true });
          const skillYaml = fs.readFileSync(path.join(rootDir, 'agents', 'opencode', 'skill.yaml'), 'utf-8');
          fs.writeFileSync(path.join(opencodeDir, 'skill.yaml'), skillYaml, 'utf-8');
          console.log(`[✓] OpenCode Skill configured -> ${opencodeDir}`);
          break;
        }
        default:
          console.log(`[!] Unknown platform: ${plat}. Supported: ${SUPPORTED_PLATFORMS.join(', ')}`);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[✗] Failed to initialize ${plat}: ${msg}`);
    }
  }

  console.log('\n[✓] Skill setup complete. You can now use knowme-careerforge in your agent workflows!');
}
