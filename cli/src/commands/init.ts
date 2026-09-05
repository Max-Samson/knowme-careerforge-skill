/**
 * KnowMe CareerForge CLI — Init Command
 * 一键将 Skill 完整工具包注入并配置至指定 AI Agent 平台环境。
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

function copyDirRecursive(src: string, dest: string): void {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist') continue;
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function copyRuntimeBundle(rootDir: string, destination: string): void {
  fs.mkdirSync(destination, { recursive: true });
  for (const directory of ['scripts', 'src', 'references']) {
    copyDirRecursive(path.join(rootDir, directory), path.join(destination, directory));
  }
  for (const file of ['SKILL.md', 'skill.json', 'package.json']) {
    fs.copyFileSync(path.join(rootDir, file), path.join(destination, file));
  }
  // npm archives omit package-lock.json; source checkouts can retain a locked install.
  const lock = path.join(rootDir, 'package-lock.json');
  const installedLock = path.join(destination, 'package-lock.json');
  if (fs.existsSync(lock)) fs.copyFileSync(lock, installedLock);
  else fs.rmSync(installedLock, { force: true });
  console.log(`Runtime files copied -> ${destination}`);
  console.log(`Prepare dependencies in that directory: npm ${fs.existsSync(lock) ? 'ci' : 'install'} --omit=dev`);
  console.log('Then run: node scripts/rendering/browser-engine.js --check-runtime');
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

  let failures = 0;
  for (const plat of targetPlatforms) {
    try {
      switch (plat) {
        case 'claude': {
          const claudeDir = path.join(homeDir, '.claude', 'skills', 'knowme-careerforge');
          copyRuntimeBundle(rootDir, claudeDir);
          console.log(`[✓] Claude Code Skill files installed -> ${claudeDir}`);
          break;
        }
        case 'codex': {
          const codexDir = path.join(homeDir, '.codex', 'skills', 'knowme-careerforge');
          copyRuntimeBundle(rootDir, codexDir);
          if (fs.existsSync(path.join(rootDir, 'agents', 'codex', 'knowme-careerforge.yaml'))) {
            fs.copyFileSync(path.join(rootDir, 'agents', 'codex', 'knowme-careerforge.yaml'), path.join(codexDir, 'skill.yaml'));
          }
          console.log(`[✓] Codex Native Skill files installed -> ${codexDir}`);
          break;
        }
        case 'cursor': {
          const cursorRulesDir = path.join(projectDir, '.cursor', 'rules');
          fs.mkdirSync(cursorRulesDir, { recursive: true });
          const runtimeDir = path.join(projectDir, '.knowme', 'skills', 'knowme-careerforge');
          copyRuntimeBundle(rootDir, runtimeDir);
          const mdcContent = fs.readFileSync(path.join(rootDir, 'agents', 'cursor', 'knowme-careerforge.mdc'), 'utf-8');
          fs.writeFileSync(path.join(cursorRulesDir, 'knowme-careerforge.mdc'), mdcContent + `\nRuntime entry: ${JSON.stringify(path.join(runtimeDir, 'SKILL.md'))}\n`, 'utf-8');
          console.log(`[✓] Cursor MDC Rule configured -> ${path.join(cursorRulesDir, 'knowme-careerforge.mdc')}`);
          break;
        }
        case 'windsurf': {
          const windsurfRulePath = path.join(projectDir, '.windsurfrules');
          const runtimeDir = path.join(projectDir, '.knowme', 'skills', 'knowme-careerforge');
          copyRuntimeBundle(rootDir, runtimeDir);
          const ruleContent = fs.readFileSync(path.join(rootDir, 'agents', 'windsurf', 'knowme-careerforge.rules'), 'utf-8');
          const begin = '<!-- knowme-careerforge:start -->';
          const end = '<!-- knowme-careerforge:end -->';
          const previous = fs.existsSync(windsurfRulePath) ? fs.readFileSync(windsurfRulePath, 'utf-8') : '';
          const block = `${begin}\n${ruleContent}\nRuntime entry: ${JSON.stringify(path.join(runtimeDir, 'SKILL.md'))}\n${end}`;
          const managed = /<!-- knowme-careerforge:start -->[\s\S]*?<!-- knowme-careerforge:end -->/;
          fs.writeFileSync(windsurfRulePath, managed.test(previous) ? previous.replace(managed, () => block) : previous + `\n\n${block}\n`, 'utf-8');
          console.log(`[✓] Windsurf Rule configured -> ${windsurfRulePath}`);
          break;
        }
        case 'gemini': {
          const geminiDir = path.join(homeDir, '.gemini', 'skills');
          fs.mkdirSync(geminiDir, { recursive: true });
          const runtimeDir = path.join(geminiDir, 'knowme-careerforge');
          copyRuntimeBundle(rootDir, runtimeDir);
          const geminiConfig = JSON.parse(fs.readFileSync(path.join(rootDir, 'agents', 'gemini', 'knowme-careerforge.json'), 'utf-8'));
          geminiConfig.entrypoint = path.join(runtimeDir, 'SKILL.md');
          fs.writeFileSync(path.join(geminiDir, 'knowme-careerforge.json'), JSON.stringify(geminiConfig, null, 2) + '\n', 'utf-8');
          console.log(`[✓] Gemini CLI Skill configured -> ${path.join(geminiDir, 'knowme-careerforge.json')}`);
          break;
        }
        case 'opencode': {
          const opencodeDir = path.join(projectDir, '.opencode', 'skills', 'knowme-careerforge');
          copyRuntimeBundle(rootDir, opencodeDir);
          console.log(`[✓] OpenCode Skill files installed -> ${opencodeDir}`);
          break;
        }
        default:
          failures += 1;
          console.log(`[!] Unknown platform: ${plat}. Supported: ${SUPPORTED_PLATFORMS.join(', ')}`);
      }
    } catch (err: unknown) {
      failures += 1;
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[✗] Failed to initialize ${plat}: ${msg}`);
    }
  }

  if (failures) {
    process.exitCode = 1;
    console.error(`[✗] ${failures} platform setup(s) failed.`);
  } else {
    console.log('Configuration and runtime files installed. Prepare dependencies and check runtime before generating PDFs; host discovery must be verified separately.');
  }
}
