# Changelog

All notable changes to the **KnowMe CareerForge** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
