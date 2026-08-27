# ADR-0001: HTML as the Sole Intermediate Working Canvas

## Status
Accepted

## Context
Traditional AI resume generators output raw Markdown and pipe it through external pandoc/typst/LaTeX tools, or directly generate binary PDF/Word files. This approach causes multiple severe failures:
1. Markdown lacks physical paged media layout capabilities (multi-column splits, exact line height tightening, A4 page break avoidance);
2. Word (.doc/.docx) and LaTeX toolchains have heavy runtime dependencies and fragile cross-platform rendering;
3. Binary formats prevent the AI Agent from inspecting DOM bounding boxes or tuning spacing parameters for self-healing page fit.

## Decision
We establish **`workspace/resume.html` as the SOLE Intermediate Working Canvas**. All tailoring, keyword highlighting, CSS Design Token calibration, and Dual QA inspections happen directly on this single, self-contained HTML file before a single deterministic PDF export step.

## Consequences
### Positive
- Zero heavy runtime dependencies (standard browser rendering engine);
- Complete physical A4 control via CSS Paged Media (`@page { size: A4; margin: 0; }` and `break-inside: avoid`);
- AI Agent can easily inspect DOM height and adjust `:root` CSS variables for automated self-healing.

### Negative / Trade-offs
- Requires maintaining clean, semantic HTML5 templates rather than simple Markdown text templates.
