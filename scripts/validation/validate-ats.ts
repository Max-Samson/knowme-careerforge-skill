#!/usr/bin/env ts-node
/** Basic text availability is part of the same final-PDF acceptance gate. */
import engine = require('../rendering/engine-loader');
import type { EngineOptions, EngineResult } from '../rendering/browser-engine';

export function validateAts(htmlPath: string, expectedPages = 1, options: EngineOptions = {}): Promise<EngineResult> {
  return engine.run(htmlPath, { ...options, expectedPages });
}
if (require.main === module) engine.cli();
