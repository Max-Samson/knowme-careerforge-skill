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
# Run one-shot end-to-end forge pipeline
python3 scripts/pipeline/forge.py --repo . --role "AI Agent Engineer" --template modern --quiet

# Extract codebase & Git evidence (repo-to-resume)
python3 scripts/evidence/extract-evidence.py --repo . --output workspace/evidence-master.json

# Analyze target Job Description
python3 scripts/evidence/analyze-jd.py --jd examples/ai-engineer/jd.md

# Search templates via CLI
python3 scripts/template/search-template.py "AI Agent Engineer" --style "two-column-split"

# Instantiate HTML working canvas with profile data
python3 scripts/template/instantiate-resume.py --template modern --profile workspace/evidence-master.json

# Validate working canvas layout & ATS compliance
python3 scripts/validation/validate-resume.py --html workspace/resume.html --expected-pages 1

# Render deterministic PDF via multi-strategy auto-discovery
python3 scripts/rendering/render-pdf.py workspace/resume.html workspace/resume.pdf

# Run all automated tests
python3 scripts/build/run-all-tests.py

# Recompile knowledge index & rebuild gallery
python3 scripts/build/build-knowledge.py
python3 scripts/build/build-gallery.py
```

See `scripts/Agent.md` for complete domain architecture and invocation standards.

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
