#!/usr/bin/env node
'use strict';
const engine = require('../rendering/browser-engine.js');
module.exports = engine;
if (require.main === module) engine.cli();
