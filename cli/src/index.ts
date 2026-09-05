#!/usr/bin/env ts-node
/**
 * KnowMe CareerForge CLI — Main Entry Point
 */

import * as child_process from 'child_process';
import * as path from 'path';
import { runInit } from './commands/init';
import { runList } from './commands/list';

function findPackageRoot(startDir: string): string {
  let curr = startDir;
  for (let i = 0; i < 6; i++) {
    if (require('fs').existsSync(path.join(curr, 'src', 'templates')) && require('fs').existsSync(path.join(curr, 'SKILL.md'))) {
      return curr;
    }
    curr = path.dirname(curr);
  }
  return path.resolve(startDir, '../../..');
}
function getVersion(rootDir: string): string {
  try {
    const pkgJson = path.join(rootDir, 'package.json');
    if (require('fs').existsSync(pkgJson)) {
      const data = JSON.parse(require('fs').readFileSync(pkgJson, 'utf-8'));
      return data.version || '0.0.6';
    }
  } catch {}
  return '0.0.6';
}

export function showHelp(): void {
  console.log(`
======================================================================
  KnowMe CareerForge CLI — Know Yourself. Define Your Direction.
======================================================================

Usage:
  knowme <command> [options]

Commands:
  forge                 Isolated user facts -> variant -> canvas -> verified PDF
  render                Multi-strategy deterministic A4 PDF export
  init                  Install and configure Skill for AI Agent platforms (cursor, claude, codex, windsurf, gemini, opencode)
  list                  Display all available role profiles and HTML templates
  search <role>         Search and rank templates for a specific role (e.g. knowme search "AI Agent Engineer")
  validate              Validate working canvas HTML layout & ATS compliance
  gallery               Build & refresh static HTML template gallery
  test                  Run full automated test suite
  help                  Show this help message

Options (for forge):
  --profile-json <file> User/Agent prepared facts or Master document
  --workspace <dir>    Parent for isolated run directories (default: workspace/runs)
  --draft              Create a draft canvas without PDF delivery
  --role <title>        Target role title
  --jd <file|text>      Target job description
  --template, -t <id>   Template ID (minimal, modern, executive, classic, academic-research, international-flow, creative-tech, compact-dense, startup-generalist, data-analyst)
  --name <name>         Candidate name override
  --output, -o <path>   Optional verified PDF copy (default: isolated run)
  --font-preset <name>  system or arial-unicode (requires local Arial Unicode MS)
  --auto-heal           Enable heuristic token auto-healing to eliminate A4 height overflow
  --quiet, -q           Quiet execution (compact JSON output)
Examples:
  knowme forge --profile-json candidate.json --role "AI Agent Engineer" --template modern
  knowme render workspace/resume.html workspace/resume.pdf
  knowme init --ai codex
  knowme init --all
`);
}

export function main(): void {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  const rootDir = findPackageRoot(__dirname);

  switch (command) {
    case 'forge': {
      let scriptPath = path.join(rootDir, 'scripts', 'pipeline', 'forge.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'forge.py');
      const passArgs = args.slice(1);
      const proc = child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case 'extract': {
      console.error('Repository-to-resume extraction is not supported. Use user-provided facts with forge --profile-json.');
      process.exitCode = 1;
      break;
    }
    case 'render': {
      let scriptPath = path.join(rootDir, 'scripts', 'rendering', 'render-pdf.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'render-pdf.py');
      const passArgs = args.slice(1);
      const proc = child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case 'init': {
      let platform = 'cursor';
      let all = false;
      let projectDir = process.cwd();

      for (let i = 1; i < args.length; i++) {
        if (args[i] === '--ai' || args[i] === '-a') {
          platform = args[i + 1] || 'cursor';
          i++;
        } else if (args[i] === '--all') {
          all = true;
        } else if (args[i] === '--project' || args[i] === '-p') {
          projectDir = args[i + 1] || process.cwd();
          i++;
        }
      }

      runInit({ platform, all, projectDir });
      break;
    }
    case 'list':
      runList();
      break;
    case 'search': {
      let scriptPath = path.join(rootDir, 'scripts', 'template', 'search-template.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'search-template.py');
      const passArgs = args.slice(1);
      const proc = child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case 'validate': {
      let scriptPath = path.join(rootDir, 'scripts', 'validation', 'validate-resume.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'validate-resume.py');
      const passArgs = args.slice(1);
      const proc = child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case 'gallery': {
      let scriptPath = path.join(rootDir, 'scripts', 'build', 'build-gallery.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'build-gallery.py');
      const proc = child_process.spawnSync('python3', [scriptPath], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case 'test': {
      let scriptPath = path.join(rootDir, 'scripts', 'build', 'run-all-tests.py');
      if (!require('fs').existsSync(scriptPath)) scriptPath = path.join(rootDir, 'scripts', 'run-all-tests.py');
      const proc = child_process.spawnSync('python3', [scriptPath], { stdio: 'inherit' });
      if (proc.status !== 0) process.exit(proc.status || 1);
      break;
    }
    case '--version':
    case '-v':
    case 'version': {
      console.log(getVersion(rootDir));
      break;
    }
    case 'help':
    case '--help':
    case '-h':
    default:
      showHelp();
      break;
  }
}

if (require.main === module) {
  main();
}
