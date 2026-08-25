# NPM Build, Publishing & Update Guide

This document explains how to build, test, version, publish, and update the **`knowme-careerforge-skill`** package on the official [NPM Registry](https://www.npmjs.com/).

---

## 1. Prerequisites

Before publishing for the first time:

1. **Create an NPM Account**: Sign up at [npmjs.com](https://www.npmjs.com/).
2. **Authenticate Locally**:
   ```bash
   npm login
   ```
3. **Verify Login**:
   ```bash
   npm whoami
   ```

---

## 2. Package Architecture & Whitelist

When publishing, NPM only packages files declared in `"files"` in `package.json`:

```json
"files": [
  "bin",        // Standalone executable (bin/knowme.js)
  "dist",       // Compiled TypeScript CLI (dist/cli/src/index.js)
  "src",        // Source of Truth: knowledge, templates, workflows, references
  "scripts",    // Core engines: search, analyze, instantiate, validate, render
  "agents",     // Platform adapter configs (Claude, Codex, Cursor, Windsurf, Gemini, OpenCode)
  "SKILL.md",   // Agent reasoning contract
  "skill.json"  // Skill manifest metadata
]
```

---

## 3. Automated One-Command Release Flow

We provide an automated release engine (`scripts/release.py`) that handles version synchronization, compilation, template gallery rebuilding, full-chain test validation, and packaging checks.

### Releasing a New Version (e.g. `1.0.1`):

```bash
# Step 1: Run the automated release pipeline
npm run release -- 1.0.1
# Or directly:
python3 scripts/release.py 1.0.1
```

The script automatically executes:
1. Version synchronization across `package.json`, `pyproject.toml`, `skill.json`, and `cli/package.json`.
2. Knowledge base compilation (`scripts/build-knowledge.py`).
3. HTML template gallery generation (`scripts/build-gallery.py`).
4. TypeScript CLI compilation (`npm run build` -> `dist/`).
5. Full-chain automated test suite execution (21/21 tests).
6. NPM packaging dry-run inspection (`npm pack --dry-run`).

---

## 4. Publishing to NPM Registry

After the release script passes with 100% success:

```bash
# 1. Commit and tag the new version
git add .
git commit -m "chore(release): bump version to v1.0.1"
git tag v1.0.1
git push origin main --tags

# 2. Publish to the public NPM registry
npm publish --access public
```

---

## 5. Verifying the Published Package

Once published, verify that the package is live and immediately accessible via `npx`:

```bash
# Check registry metadata
npm view knowme-careerforge-skill

# Test zero-install CLI execution in any directory
npx knowme-careerforge-skill@latest list
npx knowme-careerforge-skill@latest search "AI Agent Engineer"
```

---

## 6. Updating an Existing Release

When making patches or adding new templates:

| Release Type | Command | Example Version | When to Use |
| :--- | :--- | :--- | :--- |
| **Patch** | `npm run release -- 1.0.1` | `1.0.0` -> `1.0.1` | Bug fixes, typo corrections, template token tweaks |
| **Minor** | `npm run release -- 1.1.0` | `1.0.1` -> `1.1.0` | New templates, new role profiles, new CLI commands |
| **Major** | `npm run release -- 2.0.0` | `1.1.0` -> `2.0.0` | Breaking schema changes, major workflow restructuring |
