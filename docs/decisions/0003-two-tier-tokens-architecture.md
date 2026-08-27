# ADR-0003: Two-Tier Token Architecture (Primitives + Components)

## Status
Accepted

## Context
Initial iterations of the skill defined flat `--resume-*` tokens duplicated across every template's `style.css`. This caused ~60% CSS code redundancy (identical reset, identical body rules, identical Slate color codes, identical `@page` print rules) and made adding new templates error-prone.

## Decision
We establish a **Two-Tier Design Tokens Architecture**:
1. **Primitive Tokens (`src/templates/common/base.css`)**: Raw color scales (Slate, Blue, Teal, Navy), font-family stacks, 2pt spacing ladder (`--primitive-space-1` ~ `--primitive-space-12`), and universal A4 box-model reset;
2. **Component Tokens (`src/templates/{template}/style.css`)**: Semantic bindings and template-specific variables (`--resume-color-accent: var(--primitive-color-blue-600);`).

During template instantiation, `instantiate-resume.py` inlines `base.css` followed by `style.css` into the working canvas.

## Consequences
### Positive
- **High Code Reuse**: Eliminates 60% of boilerplate across templates (template `style.css` size reduced from 230 lines to 80~120 lines);
- **Standardized Spacing Ladder**: Agent self-healing selects valid discrete steps from `--primitive-space-*` rather than guessing arbitrary pixel numbers;
- **Preserved Canvas Invariant**: The resulting `workspace/resume.html` remains a 100% self-contained single file.
