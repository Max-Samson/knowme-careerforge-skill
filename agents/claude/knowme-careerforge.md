---
description: An agent-native skill for self-discovery, career positioning, and tailored resume engineering.
globs: ["workspace/*", "src/**/*"]
---

# KnowMe CareerForge — Claude Code Skill

Know Yourself. Define Your Direction. Forge Your Opportunity.

When activated, follow the 6-stage workflow:
1. **Know Me**: Extract candidate facts, classify into L1~L3 evidence.
2. **Define**: Establish target role, seniority, and Core Value Proposition.
3. **Understand**: Analyze target JD via `python3 scripts/analyze-jd.py`.
4. **Position**: Perform gap analysis, map evidence, design Resume Strategy.
5. **CareerForge**: Search template (`python3 scripts/search-template.py`), instantiate `workspace/resume.html`, calibrate CSS tokens.
6. **Review & Dual QA**: Run `python3 scripts/validate-resume.py`, self-heal overflow, render `workspace/resume.pdf` via `npx ts-node scripts/render-pdf.ts`.
