#!/usr/bin/env ts-node
/**
 * KnowMe CareerForge CLI — Main Entry Point
 */

import { runInit } from './commands/init';
import { runList } from './commands/list';

function showHelp(): void {
  console.log(`
KnowMe CareerForge CLI — Know Yourself. Define Your Direction. Forge Your Opportunity.

Usage:
  knowme <command> [options]

Commands:
  init      Install and configure Skill for AI Agent platforms (claude, cursor, codex, windsurf, gemini, opencode)
  list      Display all available role profiles and HTML templates
  help      Show this help message

Options (for init):
  --ai <platform>   Target platform (claude, codex, cursor, windsurf, gemini, opencode)
  --all             Install to all supported platforms
  --project <dir>   Target project directory (for Cursor / Windsurf / OpenCode)

Examples:
  npx ts-node cli/src/index.ts init --ai cursor
  npx ts-node cli/src/index.ts init --all
  npx ts-node cli/src/index.ts list
`);
}

function main(): void {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  switch (command) {
    case 'init': {
      let platform = 'cursor';
      let all = false;
      let projectDir = process.cwd();

      for (let i = 1; i < args.length; i++) {
        if (args[i] === '--ai' || args[i] === '-a') {
          platform = args[i + 1];
          i++;
        } else if (args[i] === '--all') {
          all = true;
        } else if (args[i] === '--project' || args[i] === '-p') {
          projectDir = args[i + 1];
          i++;
        }
      }

      runInit({ platform, all, projectDir });
      break;
    }
    case 'list':
      runList();
      break;
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
