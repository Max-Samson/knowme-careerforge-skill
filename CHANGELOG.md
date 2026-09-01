# Changelog

All notable changes to the **KnowMe CareerForge** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [0.0.6-planned] - Planned Roadmap

### 🚀 Template Matrix Expansion (Direction 2)
- Expand 6 core new templates (`academic-research`, `international-flow`, `creative-tech`, `compact-dense`, `startup-generalist`, `data-analyst`) to reach a full 10-template baseline matrix;
- Introduce 6 official theme palette presets (Tech Blue, Deep Navy, Teal Modern, Emerald Fresh, Violet Creative, Slate Minimal) in `base.css` with one-line switching.

### 🛠️ Heuristic Token Auto-Healing Algorithm (Direction 3)
- Implement `--auto-heal` parameter in `validate-resume.py` and `forge.py` (ADR-0005) to automatically step through spacing and font-size ladders for 100% single/two-page fit in one pass.

### 💻 Live Preview & Interactive Intake Wizard (Direction 4.1 & 4.2)
- **Zero-Dependency Live Preview Server (`knowme preview` / `knowme serve`)**: Lightweight HTTP + SSE server auto-reloading browser view on `workspace/resume.html` change (ADR-0006);
- **Terminal Intake Wizard (`knowme wizard`)**: Interactive 3-turn conversational profiler for Mode D non-repo candidates, producing structured `evidence-master.json`.

---

## [0.0.5] - 2026-09-01

### 🚀 Added
- **Multi-Template Full-Field Data Backfill Engine (`scripts/template/instantiate-resume.py`)**:
  - Upgraded `render_profile_into_html` to automatically backfill structured candidate profiles across all 4 template geometries (single-column, split sidebar, executive hero banner, structured table);
  - Complete coverage for `basics` (name, title, contact, city, GitHub, value proposition summary), `skills` (skill rows, tag clouds, table matrix), `experience` (org name, role badge, date range, FAB highlights), `projects` (name, role, tech stack tags, achievements), and `education` (institution, degree, date range, GPA/honors).
- **Automated Template Auto-Selection in Forge Pipeline (`scripts/pipeline/forge.py`)**:
  - Removed hardcoded default for `--template`. When omitted, `forge.py` dynamically invokes `search_templates()` via the Hybrid scorer (70% rules + 30% BM25) to recommend the optimal template for the target role;
  - Preserved explicit `--template` flag override with highest precedence.

### 🎨 Changed
- **Emoji-Free & Formal Business Aesthetic**:
  - Eliminated all casual emojis (e.g. `📱`, `✉️`, `📍`, `🎓`, `🔗`) across all templates (`minimal`, `modern`, `executive`, `classic`);
  - Standardized on clean text labels (`.contact-label`, `.badge-label`, `.info-label`) with structured alignment for an executive, distraction-free aesthetic;
  - Removed excessive translucent bubble card borders from `executive` hero banner for a streamlined, modern contact layout.
- **Template & Generator Class Name Contract Alignment**:
  - Added complete style rules for all runtime generator classes (`.role-badge`, `.tech-tag`, `.tech-stack-tags`, `.sidebar-section`, `.experience-item`, `.project-item`, `.contact-label`, `.badge-label`) in `src/templates/modern/style.css`, `minimal/style.css`, and `classic/style.css`;
  - Codified the formal Instantiator HTML Contract in `src/templates/common/base.css`.

---

## [0.0.4] - 2026-08-28

### 🐛 Fixed
- **CLI Flag Parsing (`cli/src/index.ts`)**:
  - Added `--version`, `-v`, and `version` command options to print the package version directly instead of falling through to the help menu.
- **Template Search Engine Arguments (`scripts/template/search-template.py`)**:
  - Added support for named `--role` / `-r` options alongside positional `role` arguments, enabling both `knowme search --role "<Role>"` and `knowme search "<Role>"`.

---


## [0.0.3] - 2026-08-28

### 🚀 Added
- **4-Tier Documentation Pyramid (L0~L3)**:
  - **L0**: Primary reasoning entrypoint `SKILL.md` aligned with 6-stage deterministic workflow.
  - **L1**: `AGENT.md` (Vercel-inspired agent editorial standards, priority order, four-pass discipline, anti-pattern blacklist, and quiet execution protocol) + `CLAUDE.md` (developer cheat sheet).
  - **L2**: `ARCHITECTURE.md` (6-tier architecture, data flow, Deep Module seams) + `docs/decisions/` (ADR-0001 through ADR-0004).
  - **L3**: Consolidated `references/` (01-evidence-mining.md ~ 06-qa-and-rendering.md) strictly aligned 1:1 with the 6 workflow stages.
- **Two-Tier Design Tokens Architecture**:
  - `src/templates/common/base.css`: Standardized Primitive Tokens (Slate/Blue/Teal/Navy palettes, 2pt grid spacing scale `--primitive-space-1` ~ `--primitive-space-12`, A4 print contract `@page` & `print-color-adjust`).
  - Refactored all 4 core template `style.css` files (`minimal`, `modern`, `executive`, `classic`) to bind Component Tokens to Primitive Tokens, eliminating 60% of CSS boilerplate.
  - `scripts/template/instantiate-resume.py`: Automatically merges and inlines `base.css` + `style.css` during canvas instantiation, preserving the Single-File Self-Contained Canvas Invariant.
- **Pluggable Deep Module Search Engine (`scripts/template/search-template.py`)**:
  - Abstract `BaseTemplateScorer` interface with `WeightedRuleScorer`, pure-Python `BM25TextScorer`, and `HybridTemplateScorer` (70% rules + 30% BM25).
  - Extensible CLI supporting `--engine hybrid|weighted|bm25`.
- **Architecture Decision Records (`docs/decisions/`)**:
  - `0001-html-intermediate-canvas.md`: HTML as the sole working canvas.
  - `0002-pure-css-design-tokens-over-tailwind.md`: Pure CSS3 Design Tokens over Tailwind runtime toolchain.
  - `0003-two-tier-tokens-architecture.md`: Primitive + Component token layering.
  - `0004-decentralized-json-with-bm25-index.md`: Decentralized JSON metadata with build-time BM25 index.

### 🔄 Changed
- **Platform Adapters & Distribution Packaging**:
  - Updated `agents/` configurations (`cursor.mdc`, `windsurf.rules`, `claude.md`, `codex.yaml`) to reference `AGENT.md`, `ARCHITECTURE.md`, and `references/01~06`.
  - Updated `cli/src/commands/init.ts` to bundle `references/`, `AGENT.md`, and `ARCHITECTURE.md` during `knowme init`.
- **Full Test Suite & Pipelines**:
  - Updated tests in `tests/workflows/`, `tests/templates/`, and `tests/rendering/` to validate the new architecture, passing all 24 automated tests.

---

## [0.0.2] - 2026-08-26

### 🚀 Added
- **Codebase & Git Evidence Miner (`scripts/evidence/extract-evidence.py`)**:
  - Implemented automated repository fact extraction supporting `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, Docker, CI/CD, and Git history.
  - Generates verifiable L1~L3 evidence chains and outputs structured `workspace/evidence-master.json` candidate profiles.
- **Candidate Master Profile Schema (`src/knowledge/resume-schema.json`)**:
  - Formal JSON Schema definition for candidate basics, skills, experience, projects, education, and traceable evidence levels.
- **One-Shot Forge Pipeline (`scripts/pipeline/forge.py`)**:
  - Unified command orchestrating evidence mining, JD analysis, template matching, HTML canvas instantiation, Dual QA, and PDF export in a single run.
  - Added CLI support: `knowme forge --repo . --role "<Role>" --template modern --quiet`.
- **Multi-Strategy Auto-Discovery PDF Renderer (`scripts/rendering/render-pdf.py`)**:
  - Automatically probes and leverages Playwright Headless or system-installed browsers (Google Chrome, Microsoft Edge, Brave, Chromium) across macOS, Linux, and Windows.
- **Domain-Driven Modular Scripts Architecture**:
  - Reorganized `scripts/` into 6 dedicated domain subdirectories: `pipeline/`, `evidence/`, `template/`, `validation/`, `rendering/`, and `build/`.
- **Scripts Architecture & Agent Specification (`scripts/Agent.md`)**:
  - Comprehensive developer handbook and Agent execution contract governing modular boundaries, invocation rules, and zero-heavy-dependency standards.
- **Open Source Provenance & Typography Notices (`THIRD_PARTY_NOTICES.md`)**:
  - Documented intellectual provenance and reference project attributions (`repo-to-resume-tailor`, `ui-ux-pro-max-skill`, `ResumeSample`, `ResumeCollection`).
- **Data Injection in Canvas Instantiator (`scripts/template/instantiate-resume.py`)**:
  - Injects structured profile data (`basics`, `skills`, `experience`, `projects`) directly into HTML templates while preserving CSS Design Tokens.

### 🔄 Changed
- **Quiet Execution Protocol in `SKILL.md` & Agent Rules (`agents/*`)**:
  - Enforced background silent execution across Claude Code, Codex, Cursor, Windsurf, Gemini, and OpenCode.
  - Prohibited printing raw HTML/CSS stylesheets or creating ad-hoc verification scripts in chat.
  - Established a strict 3-part delivery format (Core Value Proposition + Top 3 Evidence Highlights + PDF Delivery Path).
- **CLI Commands Expansion (`cli/src/index.ts`)**:
  - Added `forge`, `extract`, and `render` commands with graceful modular script path resolution.
- **Full-Chain Test Suite Expansion (`tests/`)**:
  - Expanded test coverage to 24 automated tests covering evidence mining, forge pipeline, and specification verification.

### 🐛 Fixed
- **Platform-Dependent PDF Generation**: Eliminated hardcoded macOS Google Chrome paths by introducing multi-strategy cross-platform browser discovery.
- **Double Keyword Highlighting**: Fixed regex matching in `instantiate-resume.py` to prevent nested `<strong><strong>...</strong></strong>` tags.
- **Chat Verbosity & Hallucinated Placeholders**: Resolved issues where AI agents wrote redundant boilerplate scripts by providing ready-to-use CLI and Python toolchains.

---

## [0.0.1] - 2026-08-20

### 🚀 Added
- **Core Skill Concept & Architecture**:
  - Established the 6-stage deterministic workflow: *Know Me* ➔ *Define* ➔ *Understand* ➔ *Position* ➔ *CareerForge* ➔ *Review & Dual QA*.
- **4 Gold Standard HTML5/CSS3 Resume Templates**:
  - `minimal`: Single-column tech-dense layout for Backend, AI, and Systems engineers.
  - `modern`: Two-column split layout (32:68) with deep navy sidebar for Fullstack and AI practitioners.
  - `executive`: Dark banner + 33:67 split layout for Technical Directors, Architects, and Leads.
  - `classic`: Modern structured table grid layout for Enterprise, Corporate, and Civil roles.
- **Universal Resume Contract (`src/templates/common/resume-contract.md`)**:
  - Defined standard DOM hierarchy, CSS Design Tokens, and A4 print media geometry (`210mm x 297mm`, `1122.5px` baseline).
- **9 Structured Role Knowledge Profiles (`src/knowledge/roles/*.json`)**:
  - Built profiles for AI Agent Engineer, Frontend Architect, Java Backend, Node Fullstack, Android, iOS, C++ Systems, Architect, and Product Manager.
- **Template Search Engine (`scripts/template/search-template.py`)**:
  - Multi-weighted recommendation algorithm scoring Role Match (35%), Style Match (25%), ATS Tier (20%), Page Fit (10%), and Density (10%).
- **Dual QA Verification Toolchain**:
  - Layout DOM height overflow inspector (`scripts/validation/validate-layout.ts` & `validate-resume.py`).
  - ATS text flow and heading hierarchy validator (`scripts/validation/validate-ats.ts`).
- **Interactive Template Gallery Generator (`scripts/build/build-gallery.py`)**:
  - Generates static A4 live preview cards at `output/templates_gallery/index.html`.
- **Multi-Agent Distribution Ecosystem**:
  - Unified metadata standard `skill.json`.
  - Platform adapters for Claude, Codex, Cursor (`.mdc`), Windsurf (`.rules`), Gemini, and OpenCode.
- **Global CLI Tool (`cli/` & `bin/knowme.js`)**:
  - Commands for `init`, `list`, `search`, `validate`, `gallery`, and `test`.
