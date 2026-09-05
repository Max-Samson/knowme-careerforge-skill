# Changelog

All notable changes to the **KnowMe CareerForge** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [0.0.7] - 2026-09-06

This patch clarifies the resume workflow across Agent adapters, tightens guidance for faithful rewriting, and simplifies setup and delivery based on real Claude and Gemini usage.

### Added

- `browser-engine.js --check-runtime` to report missing runtime dependencies together and check browser startup without generating candidate artifacts; `READY` indicates runtime availability, not resume acceptance. Added command-line help.
- `forge.py --summary` for a compact result containing the current HTML/PDF delivery paths and manifest location, while retaining full on-disk diagnostics.
- `search-template.py --summary` for the top three ranked layouts without duplicated metadata. Existing full JSON output and ranking remain unchanged.
- Regression coverage for isolated installation, adapter entry paths, repeated setup, runtime diagnostics, compact reports and education alignment.

### Changed

- Platform adapters now route to one `SKILL.md` workflow. Intake precedes resource exploration; drafting and rendering wait for candidate material, and optional omissions no longer mandate a Draft detour.
- Rewriting guidance now compares claims with original user material, covering technologies, ownership, scope, implementation mechanisms, outcomes and certainty. Role knowledge and examples are not candidate facts; accepting a draft does not substantiate Agent-added claims.
- Default delivery presents one current resume as PDF and editable HTML, with the actual template and necessary remaining gaps. Internal snapshots and QA stay separate; focused updates preserve unrelated content, template choice and delivery filenames.
- Template guidance covers all ten layouts and prioritizes actual content and readability. Removed mandatory FAB-style outcomes and unsupported ATS keyword-density targets; clarified the separate meanings of factual review, technical PDF acceptance and visual inspection.

### Fixed

- Installed bundles missing runtime package metadata. Installers now include `package.json` and copy `package-lock.json` when available, with explicit dependency-preparation instructions.
- Cursor/Windsurf configurations lacking a bundled runtime and concrete entry path; Gemini configuration now points to its installed runtime entry.
- Installation failures being followed by an unconditional success message, and repeated Windsurf setup appending duplicate managed rules.
- Degree and major being spread across opposite ends of an education row when school or dates are absent. Actual dates remain right-aligned.

### Upgrade notes

- Re-run `knowme init --ai <platform>` with the updated package to refresh installed instructions and resources. Prepare dependencies in the installed runtime using `npm ci --omit=dev` when a lockfile is present, otherwise `npm install --omit=dev`, then run the runtime check.
- Default and `--quiet` report formats remain compatible; compact output is opt-in through `--summary`. Historical runs and verified-copy failure protections are preserved.
- Automated checks validate tool behavior and PDF output, not candidate authenticity or every host's compliance with instructions. Real-host behavior should be verified after upgrading.

---

## [0.0.6] - 2026-09-05

This release expands the template collection and improves the reliability of resume generation, from preserving supplied facts to validating the final PDF.

### Added

- Six new templates: `academic-research`, `international-flow`, `creative-tech`, `compact-dense`, `startup-generalist`, and `data-analyst`, bringing the collection to ten templates. Six theme palette presets provide additional styling options.
- Draft, Master and Variant profiles for incomplete drafts, reusable source facts and role-specific resumes, with source-version tracking.
- Isolated workspaces for each generation run, including input snapshots, editable HTML, validation reports and a delivery manifest.
- `--auto-heal` for bounded spacing and font-size adjustments. Failed adjustments preserve the original canvas; candidate facts are never rewritten to force a fit.
- `--font-preset system|arial-unicode` with font diagnostics for PDF text extraction.

### Changed

- Resume generation now explicitly uses user descriptions, existing resumes and supplied supporting material. The host Agent handles content interpretation and tailoring; the toolchain handles validation, layout and export.
- Each template has one maintained `canvas.html` structure. Gallery samples are stored separately, and previews share the same generation path and styles as actual resumes.
- Printing and PDF export share one validation engine across Python and TypeScript entry points, checking fonts, every page's layout, A4 geometry and final PDF text before publication.
- Generation results distinguish `DRAFT`, `PASS`, `FAIL` and `UNVERIFIED`. Delivery paths and accepted artifact hashes are recorded in the current run's manifest.
- Updated Skill metadata, usage guidance and architecture documentation; added an `AGENTS.md` development entry and package-design guidelines aligned with Agent Skills.
- Expanded regression coverage for profile binding, output isolation, gallery consistency and browser/PDF validation.

### Fixed

- Sample content leaking into incomplete profiles, and missing values being replaced with unsupported candidate facts.
- Education records overwriting one another and supplied experience, project or education details being lost during binding.
- Invalid template slots, unsafe text insertion and keyword highlighting corrupting generated HTML; binding failures now preserve the previous output.
- Stale PDFs being reported as successful delivery after rendering or validation failures.
- Incomplete or contradictory QA results being accepted, including estimate-based success when browser checks were unavailable.
- Gallery builds silently skipping invalid templates or samples instead of failing before publication.

### Upgrade notes

- Use `knowme forge --profile-json <file>` for structured input. Existing raw profile JSON remains supported. Repository-to-resume extraction is not supported by this workflow.
- Generated files now belong to `workspace/runs/<runId>/`. Read delivery paths from the returned manifest; use `--output` and `--html-output` when explicit copies are needed.
- Requires Python 3.9+, Node.js 22.13+, the declared npm dependencies and a compatible Chromium browser. The `arial-unicode` preset additionally requires local Arial Unicode MS.
- Each `.resume-page` represents one A4 page. `--expected-pages` sets a maximum of one or two pages; two-page layouts require explicit page containers. Automatic fitting preserves a minimum body size of 8.8pt and may report that further layout edits are needed.

### Known issues

- Platform setup is not yet uniform: some adapters install only prompt configuration, copied Skill bundles require separate runtime dependency setup, and the initializer may report completion after a partial failure. Verify the installed resources and dependencies before use. Automated PDF checks do not certify every ATS reader's interpretation of multi-column content.

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
