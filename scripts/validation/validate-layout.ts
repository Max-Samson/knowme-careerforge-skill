#!/usr/bin/env ts-node
import engine = require('../rendering/engine-loader');
import type { EngineOptions, EngineResult } from '../rendering/browser-engine';

export function validateLayout(htmlPath: string, expectedPages = 1, options: EngineOptions = {}): Promise<EngineResult> {
  return engine.run(htmlPath, { ...options, expectedPages });
}
if (require.main === module) engine.cli();
