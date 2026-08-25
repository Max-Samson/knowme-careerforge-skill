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

export function showHelp(): void {
  console.log(`
======================================================================
  KnowMe CareerForge CLI — Know Yourself. Define Your Direction.
======================================================================

Usage:
  knowme <command> [options]

Commands:
  init          Install and configure Skill for AI Agent platforms (cursor, claude, codex, windsurf, gemini, opencode)
  list          Display all available role profiles and HTML templates
  search <role> Search and rank templates for a specific role (e.g. knowme search "AI Agent Engineer")
  validate      Validate working canvas HTML layout & ATS compliance
  gallery       Build & refresh static HTML template gallery
  test          Run full automated test suite
  help          Show this help message

Options (for init):
  --ai, -a <platform>   Target platform (claude, codex, cursor, windsurf, gemini, opencode)
  --all                 Install to all supported platforms
  --project, -p <dir>   Target project directory (default: current directory)

Examples:
  npx knowme-careerforge init --ai cursor
  npx knowme-careerforge init --ai claude
  npx knowme-careerforge init --all
  npx knowme-careerforge list
  npx knowme-careerforge search "Senior Frontend Architect"
  npx knowme-careerforge validate
`);
}

export function main(): void {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  const rootDir = findPackageRoot(__dirname);

  switch (command) {
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
      const role = args[1] || 'AI Agent Engineer';
      const scriptPath = path.join(rootDir, 'scripts', 'search-template.py');
      const passArgs = args.slice(1);
      child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      break;
    }
    case 'validate': {
      const scriptPath = path.join(rootDir, 'scripts', 'validate-resume.py');
      const passArgs = args.slice(1);
      child_process.spawnSync('python3', [scriptPath, ...passArgs], { stdio: 'inherit' });
      break;
    }
    case 'gallery': {
      const scriptPath = path.join(rootDir, 'scripts', 'build-gallery.py');
      child_process.spawnSync('python3', [scriptPath], { stdio: 'inherit' });
      break;
    }
    case 'test': {
      const scriptPath = path.join(rootDir, 'scripts', 'run-all-tests.py');
      child_process.spawnSync('python3', [scriptPath], { stdio: 'inherit' });
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
