---
description: An agent-native skill for self-discovery, career positioning, and tailored resume engineering.
globs: ["workspace/*", "src/**/*", "scripts/**/*", "references/*"]
---

# KnowMe CareerForge — Claude Code Skill

> *"Know Yourself. Define Your Direction. Forge Your Opportunity."*

When activated, follow the 6-Stage Deterministic Workflow and Quiet Execution Protocol (see `AGENT.md` and `ARCHITECTURE.md`):

1. **Evidence Mining (repo-to-resume)**: Extract codebase facts via `python3 scripts/evidence/extract-evidence.py --repo .` or run one-shot `python3 scripts/pipeline/forge.py` (see `references/01-evidence-mining.md`).
2. **Define Goal & Archetype**: Establish target seniority tier and capability matrix (see `references/02-career-goal.md`).
3. **Understand Target**: Analyze target JD via `python3 scripts/evidence/analyze-jd.py` (see `references/03-jd-analysis.md`).
4. **Template Search**: Match template via `python3 scripts/template/search-template.py` (see `references/04-template-selection.md`).
5. **Intermediate Canvas**: Instantiate `workspace/resume.html` via `python3 scripts/template/instantiate-resume.py` and calibrate CSS design tokens (see `references/05-html-canvas-tokens.md`).
6. **Review & Dual QA**: Run `python3 scripts/validation/validate-resume.py` and export `workspace/resume.pdf` via `python3 scripts/rendering/render-pdf.py` (see `references/06-qa-and-rendering.md`).
7. **Quiet Delivery**: Execute silently in background; deliver concise executive summary and final file path (`workspace/resume.pdf`).
