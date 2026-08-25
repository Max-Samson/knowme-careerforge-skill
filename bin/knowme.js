#!/usr/bin/env node
/**
 * KnowMe CareerForge CLI Executable Entrypoint
 * Standalone zero-dependency executable for npx knowme-careerforge / npm global install.
 */

const path = require('path');
const fs = require('fs');

const distEntry = path.join(__dirname, '..', 'dist', 'cli', 'src', 'index.js');
const srcEntry = path.join(__dirname, '..', 'cli', 'src', 'index.ts');

if (fs.existsSync(distEntry)) {
  const cli = require(distEntry);
  if (typeof cli.main === 'function') {
    cli.main();
  }
} else if (fs.existsSync(srcEntry)) {
  try {
    require('ts-node/register');
    const cli = require(srcEntry);
    if (typeof cli.main === 'function') {
      cli.main();
    }
  } catch (e) {
    console.error('[!] Precompiled CLI not found. Please run "npm run build" first.');
    process.exit(1);
  }
} else {
  console.error('[!] KnowMe CLI entrypoint not found.');
  process.exit(1);
}
