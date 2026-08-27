# ADR-0002: Pure CSS3 Design Tokens over Tailwind Runtime Pipeline

## Status
Accepted

## Context
When styling HTML templates, modern web development frequently defaults to Tailwind CSS (either via CLI PostCSS build step or PlayCDN script). We evaluated whether Tailwind CSS or pure native CSS3 with Design Tokens is better suited for an Agent-driven resume engineering skill.

## Decision
We choose **Native HTML5 + Pure CSS3 Design Tokens (CSS Custom Properties)** and **explicitly reject Tailwind runtime compilers, PostCSS toolchains, and CDN scripts**. We internalize Tailwind's design scale (Slate neutral palette, 2pt/4px spacing scales) directly into our standard CSS variables.

## Consequences
### Positive
- **100% Offline & Deterministic**: Templates load in single-digit milliseconds inside Playwright/Chromium with zero network requests or CSS computation flashing;
- **Superior A4 Paged Media Control**: Native `@page`, `size: A4 portrait`, `margin: 0`, and `pt/mm` print units are fully supported;
- **Ultra-low Agent Calibration Cost**: To fix an overflow of 18px on a page, an Agent modifies one line (`--resume-space-section: 9.5pt;`) in `:root` rather than editing utility classes across 150+ DOM elements;
- **Zero-Dependency Core**: Running `instantiate-resume.py` requires only standard Python 3.

### Negative / Trade-offs
- Template developers must author semantic CSS classes rather than composing utility classes in HTML.
