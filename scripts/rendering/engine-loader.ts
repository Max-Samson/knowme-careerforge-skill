import * as fs from 'fs';
import * as path from 'path';
// tsc does not copy JS. Resolve the shipped source engine from source or dist.
let root = __dirname;
while (!fs.existsSync(path.join(root, 'package.json'))) {
  const parent = path.dirname(root);
  if (parent === root) throw new Error('Cannot locate browser engine project root');
  root = parent;
}
const engine: typeof import('./browser-engine') = require(path.join(root, 'scripts/rendering/browser-engine.js'));
export = engine;
