<div align="center">

# 🎯 KnowMe CareerForge

<p align="center">
  <strong>认识自己，明确方向，锻造属于你的职业机会。</strong><br>
  <em>Know Yourself. Define Your Direction. Forge Your Opportunity.</em>
</p>

<p align="center">
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/语言-🇨🇳_简体中文-0284C7?style=flat" alt="简体中文"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/Language-🇺🇸_English-4F46E5?style=flat" alt="English"></a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/knowme-careerforge-skill"><img src="https://img.shields.io/npm/v/knowme-careerforge-skill?style=flat&logo=npm&logoColor=white&color=CB3837" alt="npm version"></a>
  <img src="https://img.shields.io/badge/Node.js-%3E%3D18-339933?style=flat&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-A4_PDF-2EAD33?style=flat&logo=playwright&logoColor=white" alt="Playwright">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6B7280?style=flat" alt="MIT License"></a>
</p>

</div>
---

## 1. What is KnowMe CareerForge?

**KnowMe CareerForge** is an industrial-grade, agent-native resume engineering skill for Claude Code, Cursor, Codex, Windsurf, and Gemini CLI.

Traditional AI resume tools treat resume writing as a superficial text-generation task: feed a prompt to an LLM, get a block of Markdown, and convert it through black-box tools into a fragile, hallucination-prone PDF.

**KnowMe CareerForge** fundamentally rethinks this paradigm into a structured, dual-engine system:

```text
knowme-careerforge-skill
          │
          ▼
   KnowMe CareerForge
          │
    ┌─────┴─────┐
    ▼           ▼
  KnowMe     CareerForge
    │           │
Self Discovery  Tailored Career Story
& Evidence      & Engineering Delivery
```

- **KnowMe (Self-Discovery & Evidence Engine)**: Helps candidates discover who they are, uncover their verifiable career evidence (L1~L3), and map their true competitive strengths.
- **CareerForge (Career Positioning & Resume Engineering)**: Translates genuine strengths into targeted positioning for specific job opportunities, tailoring high-impact content inside an **HTML Intermediate Working Canvas** with **Design Tokens**, and delivering deterministic, pixel-perfect PDFs via Playwright.

---

## 2. Core Philosophy & Guiding Principle

> ### *"The goal is not to make the candidate look better than they are. The goal is to make their real strengths visible to the right opportunity."*

```text
WRONG DIRECTION (Generic AI Hallucination):
JD ──> Keyword Stuffing ──> AI Guessing ──> Superficial Fluff ──> Inflated Claims (Fragile in Interviews)

RIGHT DIRECTION (KnowMe CareerForge):
Real Experience ──> Grounded Evidence ──> True Strengths ──> Job Match ──> Precise Engineering & Narrative
```

---

## 3. Installation

You can install and use KnowMe CareerForge via **CLI (Zero Clone)** or directly through **Agent-Native Manifests**:

### Option A: Using CLI (Recommended)

Run directly with `npx` (no clone required):

```bash
# Go to your project directory
cd /path/to/your/project

# Install for your preferred AI assistant
npx knowme-careerforge-skill init --ai cursor    # Cursor (.cursor/rules/)
npx knowme-careerforge-skill init --ai claude    # Claude Code (~/.claude/skills/)
npx knowme-careerforge-skill init --ai codex     # Codex CLI (~/.codex/skills/)
npx knowme-careerforge-skill init --ai windsurf  # Windsurf (.windsurfrules)
npx knowme-careerforge-skill init --ai gemini    # Gemini CLI (~/.gemini/skills/)
npx knowme-careerforge-skill init --ai opencode  # OpenCode (.opencode/skills/)
npx knowme-careerforge-skill init --all          # All supported assistants
```

Or install globally:

```bash
npm install -g knowme-careerforge-skill
knowme init --ai cursor
knowme list
```

---

### Option B: Direct Agent Integration

| Platform | Target Configuration Path | Setup Command |
| :--- | :--- | :--- |
| **Cursor** | `.cursor/rules/knowme-careerforge.mdc` | `cp SKILL.md .cursor/rules/knowme-careerforge.mdc` |
| **Claude Code** | `~/.claude/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.claude/skills/` |
| **Codex** | `~/.codex/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.codex/skills/` |
| **Windsurf** | `.windsurfrules` | `cat agents/windsurf/knowme-careerforge.rules >> .windsurfrules` |
| **OpenCode** | `.opencode/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.opencode/skills/` |

---

## 4. The 3 Operational Modes

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Mode A: Target-Role Mode                                                    │
│ User specifies a career direction (e.g., "Senior AI Agent Engineer").       │
│ ▶ Agent loads role skill tree, extracts matching evidence, builds variant.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Mode B: JD-Specific Mode                                                    │
│ User pastes a concrete Job Description (JD).                                │
│ ▶ Agent runs analyze-jd.py, performs gap analysis, highlights hiring keys.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Mode C: Repo-to-Resume Mode                                                 │
│ User supplies a GitHub repository / codebase / project notes.               │
│ ▶ Agent inspects code/config files, grades evidence into L1~L3, builds FAB. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. End-to-End Execution Workflow

```text
  Know (Evidence L1~3) ──> Define (Goal) ──> Understand (JD Signals) ──> Position (Strategy) ──> Forge (HTML Canvas) ──> Review (Dual QA)
```

1. **[KnowMe] Evidence Mapping**: Candidate experience is analyzed and strictly categorized into L1 (Code/Config proven), L2 (Module/Dependency inferred), and L3 (Contextual inference).
2. **[Define & Understand] Signal Extraction**: The target JD is parsed to extract must-have competencies and hiring signals.
3. **[Position] Strategy Formulation**: Gap analysis maps real candidate evidence to target JD requirements.
4. **[CareerForge] Template Search & Assembly**: The best HTML template is chosen using multi-criteria BM25 ranking (`search-template.py`) and instantiated to `workspace/resume.html`.
5. **[Review & Dual QA] Self-Healing**: Layout box model height overflow and ATS textual readability tests run automatically. If an overflow is detected, CSS spacing tokens are auto-calibrated.
6. **[PDF Export] Deterministic Output**: Playwright renders pixel-perfect `workspace/resume.pdf` with `@media print` A4 rules.

---

## 6. Token Self-Healing & Visual Tuning Cheat Sheet

All visual parameters are concentrated in `:root` variables inside `workspace/resume.html`:

| CSS Token | Default | Compact (1-Page Squeeze) | Relaxed (2-Page Flow) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `--resume-space-section` | `12pt` | `9.5pt` ~ `10.5pt` | `14pt` ~ `16pt` | Section vertical gap (primary self-healing knob) |
| `--resume-space-item` | `8pt` | `6.5pt` ~ `7pt` | `9pt` ~ `11pt` | Item gap between jobs/projects |
| `--resume-font-size-body` | `9.2pt` | `8.8pt` ~ `9.0pt` | `9.5pt` ~ `10pt` | Body text size (safe legibility floor is 8.8pt) |
| `--resume-line-height-body` | `1.45` | `1.38` | `1.50` | Line height ratio |
| `--resume-color-accent` | `#2563eb` | Custom Hex | Custom Hex | Primary theme accent color |
| `--resume-sidebar-width` | `32%` | `30%` | `35%` | Sidebar width (for modern/executive templates) |

---

## 7. Core Templates Matrix

| Template ID | Style | Category | ATS Tier | Best For | Target Pages |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`minimal`** | Single-Column Minimal | Tech / AI | Tier 1 (Optimal) | Backend, Algorithms, AI Research, Systems | 1 Page |
| **`modern`** | Two-Column Split (32:68) | Tech / Fullstack | Tier 1 (Optimal) | Fullstack, AI Agent, Frontend, Global Roles | 1~2 Pages |
| **`executive`** | Executive Banner + 33:67 | Leadership / Product | Tier 1 (Optimal) | Tech Director, Chief Architect, Tech Lead | 1~2 Pages |
| **`classic`** | Structured Table Grid | Corporate / Gov | Tier 1 (Optimal) | State Enterprises, Finance, Hardware, Civil | 1 Page |

---

## 8. CLI & Script Reference

```bash
# 1. One-shot resume engineering pipeline (mining -> canvas -> QA -> PDF)
knowme forge --repo . --role "AI Agent Engineer" --template modern --quiet

# 2. Search best template for target role (hybrid engine)
knowme search --role "AI Agent Engineer" --engine hybrid

# 3. Extract candidate evidence & facts from codebase
knowme extract --repo . --output workspace/evidence-master.json

# 4. Validate working canvas layout & ATS compliance
knowme validate

# 5. Render deterministic pixel-perfect PDF
knowme render --input workspace/resume.html --output output/resume.pdf

# 6. Build & view static HTML Template Gallery
knowme gallery
```
---

## Automated Test Suite

```bash
npm test
# Or:
python3 scripts/build/run-all-tests.py
```
---

## 10. NPM Build, Release & Publishing

This package is ready to be built, tested, and published to the NPM Registry:

```bash
# 1. Automated release preparation & verification
npm run release -- 0.0.4

# 2. Publish to public NPM registry
npm publish --access public
```

See the full [NPM Publishing & Update Guide](docs/PUBLISHING.md) for step-by-step release instructions.

---

## 11. License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
