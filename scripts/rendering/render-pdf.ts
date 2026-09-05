#!/usr/bin/env ts-node
import engine = require('./engine-loader');
import type { EngineOptions, EngineResult } from './browser-engine';

export async function renderResumePdf(options: EngineOptions & { inputHtml: string; outputPdf: string }): Promise<EngineResult> {
  const result = await engine.run(options.inputHtml, options);
  if (result.status !== 'PASS') throw new Error(JSON.stringify(result));
  return result;
}
if (require.main === module) engine.cli(process.argv.slice(2), { outputPdf: 'workspace/resume.pdf' });
