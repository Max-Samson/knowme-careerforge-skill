---
description: An agent-native skill for self-discovery, career positioning, and tailored resume engineering.
globs: ["workspace/*", "src/**/*", "scripts/**/*"]
---

# KnowMe CareerForge — Claude Code Skill

Know Yourself. Define Your Direction. Forge Your Opportunity.

When activated, follow the Evidence-First & Quiet Execution Protocol (see `scripts/Agent.md`):
1. **Evidence Mining (repo-to-resume)**: Extract codebase facts via `python3 scripts/evidence/extract-evidence.py --repo .` or run one-shot `python3 scripts/pipeline/forge.py`.
2. **Understand Target**: Analyze target JD via `python3 scripts/evidence/analyze-jd.py`.
3. **Template Search**: Match template (`python3 scripts/template/search-template.py`).
4. **Intermediate Canvas**: Instantiate `workspace/resume.html` via `python3 scripts/template/instantiate-resume.py` and calibrate CSS design tokens.
5. **Review & Dual QA**: Run `python3 scripts/validation/validate-resume.py`.
6. **PDF Delivery**: Export `workspace/resume.pdf` via `python3 scripts/rendering/render-pdf.py`.
7. **Quiet Delivery**: Execute silently in background; deliver concise executive summary and final file path (`workspace/resume.pdf`).
