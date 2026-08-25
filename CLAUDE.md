# KnowMe CareerForge — Agent Developer Guide

Welcome, AI Coding Assistant! This file provides key conventions, architecture guidelines, and build commands for working inside `knowme-careerforge-skill`.

---

## 1. Project Overview & Invariants

- **Mission**: Evidence-first career positioning and tailored resume engineering.
- **Core Philosophy**: *"The goal is not to make the candidate look better than they are. The goal is to make their real strengths visible to the right opportunity."*
- **Canvas Invariant**: `workspace/resume.html` is the SOLE Intermediate Working Canvas. All edits, token tweaks, and QA checks happen on this file before exporting to `workspace/resume.pdf`.
- **Zero-Dependency Rule**: The templates and core scripts must remain lightweight, using standard Python 3 and pure HTML5/CSS3 Design Tokens without complex build toolchains (no PostCSS/Tailwind runtime pipelines).

---

## 2. Essential Commands

```bash
# Run all automated tests (Templates, ATS, Workflows, End-to-End Pipeline)
python3 scripts/run-all-tests.py

# Run individual test modules
python3 -m unittest tests/templates/test_templates.py
python3 -m unittest tests/ats/test_ats.py
python3 -m unittest tests/workflows/test_workflows.py
python3 -m unittest tests/rendering/test_smoke.py

# Recompile knowledge index & templates registry
python3 scripts/build-knowledge.py

# Rebuild interactive HTML template gallery
python3 scripts/build-gallery.py

# Search templates via CLI
python3 scripts/search-template.py "AI Agent Engineer" --style "two-column-split"

# Validate working canvas layout & ATS compliance
python3 scripts/validate-resume.py --html workspace/resume.html --expected-pages 1

# Render deterministic PDF via Playwright
npx ts-node scripts/render-pdf.ts --input workspace/resume.html --output workspace/resume.pdf
```

---

## 3. Code & Architecture Standards

1. **TypeScript**:
   - Strict mode enabled (`tsconfig.json`).
   - Never use `any` or `as any` (enforce `ts-no-any` rule; use `unknown`, type narrowing, or specific domain types).
2. **Python**:
   - Target Python 3.9+.
   - Use standard library exclusively for core runtime engines (`scripts/`).
   - Enforce clean error handling with `try...except` and structured JSON outputs.
3. **HTML / CSS**:
   - 100% semantic tags conforming to `src/templates/common/resume-contract.md`.
   - All visual spacing, typography, and colors MUST be declared in `:root` as CSS variables (`--resume-*`).
   - Enforce physical A4 dimensions: `width: 210mm; min-height: 297mm;` and `@page { size: A4 portrait; margin: 0; }`.
