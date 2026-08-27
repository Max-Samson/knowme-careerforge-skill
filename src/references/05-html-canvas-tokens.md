# Reference Manual 05: HTML Canvas Engineering & Design Tokens

> **"workspace/resume.html is the SOLE Intermediate Working Canvas. All modifications, tailoring, and token tuning happen here."**

---

## 1. Two-Tier Design Tokens Architecture

```
┌────────────────────────────────────────────────────────┐
│ 1. Primitive Tokens (Declared in common/base.css)       │
│    Raw colors, 2pt spacing ladder, font-family, A4 size│
├────────────────────────────────────────────────────────┤
│                          ▼                             │
│ 2. Component Tokens (Declared in template style.css)   │
│    --resume-space-section, --resume-font-size-body...  │
└────────────────────────────────────────────────────────┘
```

### 1.1 Primitive Spacing Scale (2pt Base Grid):
- `--primitive-space-1`: `2pt` (Bullet margins, micro tags)
- `--primitive-space-2`: `4pt` (Tag padding, avatar margins)
- `--primitive-space-3`: `6pt` (Title-to-line gaps)
- `--primitive-space-4`: `8pt` (Item margins)
- `--primitive-space-5`: `10pt` (Section header bottom margins)
- `--primitive-space-6`: `12pt` (Section margins)
- `--primitive-space-8`: `16pt` (Outer page padding gaps)

### 1.2 Calibratable Component Tokens:
Agent is strictly authorized to calibrate these CSS variables in `<style>` of `workspace/resume.html`:

| CSS Variable | Default Value | Overflow Remedy (-1.0 Page Fit) |
|:---|:---|:---|
| `--resume-space-section` | `11pt` ~ `12pt` | Reduce to `9.0pt` ~ `10pt` |
| `--resume-space-item` | `7.5pt` ~ `8.0pt` | Reduce to `6.0pt` ~ `6.5pt` |
| `--resume-space-bullet` | `2.5pt` ~ `3.0pt` | Reduce to `1.5pt` ~ `2.0pt` |
| `--resume-font-size-body` | `9.2pt` | Reduce to `8.8pt` ~ `9.0pt` |
| `--resume-line-height-body` | `1.45` | Reduce to `1.38` ~ `1.40` |

---

## 2. Canvas Editing Rules & Invariants

1. **Single-File Self-Contained Invariant**: `workspace/resume.html` contains inlined CSS and no external network font/script dependencies;
2. **Semantic HTML Tags Contract**:
   - Page Root: `<div class="resume-page" id="page-1">`
   - Candidate Header: `h1.candidate-name`, `p.job-target`
   - Sections: `section.resume-section` with `h2.section-title`
   - Experience/Projects: `div.experience-item`, `div.project-item`
   - Bullets: `ul.bullet-list > li` with bold key phrases `<strong>`
3. **Fact Invariant**: Never edit historical dates, company names, or verified achievements to fit a layout; adjust spacing tokens and condense wording instead.
