# KnowMe CareerForge — System Architecture & Design Specification

> **Positioning**: An agent-native skill for candidate self-discovery, career positioning, and tailored resume engineering across mainstream AI coding assistants (Claude Code, Codex, Cursor, Windsurf, Gemini CLI, Copilot, OpenCode).
>
> **Core Paradigms**: User-Supplied Facts & Traceable Provenance · HTML Intermediate Working Canvas · Two-Tier Design Tokens · Pluggable Hybrid Search · Deterministic PDF Closed-Loop

---

The host Agent collects and interprets user-supplied experience, existing resumes and explicitly supplied supporting material, then tailors wording to the target role. Tools validate structured data, bind HTML, measure print output and accept the final PDF. Repository analysis is not a supported resume input path. Optional legacy L1~L3 labels describe provenance, not independent verification.

This document preserves the system design and module boundaries. `AGENT.md` governs AI development and architecture changes in this repository; `SKILL.md` governs using the Skill to create resumes. Current lifecycle, field and error semantics are defined in [references/07-artifact-contract.md](references/07-artifact-contract.md); roadmap documents describe planned work and must not be treated as implemented capabilities.

## 1. The 4-Tier Documentation Pyramid

KnowMe CareerForge adopts a progressive 4-tier documentation architecture to ensure clean separation of concerns between agent execution, developer maintenance, architectural governance, and runtime rules:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        KnowMe CareerForge 4-Tier Documentation Pyramid                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ L0: Platform Distribution │ SKILL.md (Agent 6-Stage Reasoning Contract) + skill.json   │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ L1: Agent & Dev Contracts │ CLAUDE.md (Developer Command Cheat Sheet & Guidelines)     │
│                           │ AGENT.md (AI Development & Architecture Guidelines)│
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ L2: Architecture & ADRs   │ ARCHITECTURE.md (6-Tier Architecture, Seams, Data Flow)    │
│                           │ docs/decisions/ (Architecture Decision Records - ADRs)     │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ L3: Runtime Domain Assets │ references/ (01-evidence-mining.md ~ 07-artifact-contract.md)  │
│ (Source of Truth)         │ src/templates/ (canvas.html + shared/template CSS)      │
│                           │ src/knowledge/ (roles/*.json, layouts.json, styles.json)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six-Layer System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Multi-Agent Ecosystem Layer (Distribution & Adapters)                    │
│    Claude Code | Codex | Cursor (.mdc) | Windsurf | Gemini CLI | OpenCode   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ CLI Dynamic Config Injection
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 2. Skill Execution Core Layer (Agent Reasoning Contract)                     │
│    SKILL.md (6-Stage Pipeline) │ AGENT.md (Development & Architecture Rules)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Python Toolchain / CLI Invocation
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 3. Retrieval & Reasoning Engine Layer (Deep Modules in scripts/)            │
│    search-template.py (Hybrid/BM25) │ instantiate-resume.py (Slot Binding)   │
│    forge.py (Run Orchestration)    │ analyze-jd.py (Signal & Keyword Parser)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Structured Schema Data
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 4. Structured Knowledge & Data Assets Layer (src/knowledge/ - SSoT)         │
│    roles/*.json (9+ Role Profiles)  │ layouts.json │ styles.json            │
│    resume-schema.json (Shared Profile Schema)│ ats-rules.json                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Instantiation into Intermediate Canvas
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 5. HTML Resume Template & Token Engine Layer (src/templates/)               │
│    common/base.css (Primitives & A4 Print) │ minimal/ │ modern/ │ classic/  │
│    executive/ │ CSS Variables Two-Tier Hierarchy (--primitive-* / --resume-*)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Dual QA & Headless Browser Rendering
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 6. Rendering & Automated QA Closed-Loop Layer                                │
│    validate-resume.py (Print DOM + PDF) │ validate-ats.ts (Text Stream QA)   │
│    browser-engine.js (Shared Print Measurement & Final PDF Acceptance)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. End-to-End Deterministic Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate / User
    participant Agent as Host Agent
    participant Engine as Forge & Profile Toolchain
    participant Browser as Shared Browser Engine

    User->>Agent: Experience, existing resume, supporting material, target JD
    Agent->>Agent: Organize Draft, clarify needed facts, prepare Master
    Agent->>Engine: Analyze JD and select template
    Agent->>Engine: forge.py --profile-json master.json
    Engine->>Engine: Create unique run, snapshot input, validate profile
    Engine->>Engine: Save Master and source-linked Variant
    Engine->>Engine: Bind canvas.html with full CSS chain
    Engine->>Browser: Measure print DOM for all pages
    Browser->>Browser: Generate fresh PDF; inspect geometry and per-page text
    alt Required checks and final PDF acceptance pass
        Browser-->>Engine: Publish accepted bytes and hashes
        Engine-->>Agent: PASS manifest and current-run artifacts
        Agent->>Agent: Review facts, typography and reading order
        Agent-->>User: Deliver artifact links and review outcome
    else Validation fails or cannot complete
        Browser-->>Engine: FAIL or UNVERIFIED with diagnostics
        Engine-->>Agent: Retained run and error manifest; no delivery outputs
        Agent-->>User: Actual status and corrective next step
    end
```

The host Agent owns semantic editing and evidence selection. The current forge script preserves supplied entries and applies explicit basic-field/title overrides; it does not autonomously infer a career narrative from repositories. Draft mode produces a draft canvas without final PDF acceptance. Manual canvas edits remain editable artifacts; do not overwrite them by replaying stale input.

Each invocation creates `workspace/runs/<runId>/` containing the input snapshot, Master/Variant (or Draft), HTML, QA, manifest and an accepted PDF when successful. `--workspace` changes the parent, not run isolation. Master and Variant are independent documents linked by a normalized profile hash, which tracks versions rather than truth. Missing/null optional fields remain unknown; malformed types and unknown fields fail. Supplied education, work and project arrays are preserved independently.

The current manifest is authoritative: `RUNNING` is intermediate, `DRAFT` is not PDF acceptance, `PASS` records accepted artifacts, `FAIL` denotes a rejected operation, and `UNVERIFIED` denotes unavailable or incomplete checking. Old output existence cannot imply success. See the artifact contract for exit codes and required report fields.


---

## 4. Deep Module Seams & Interface Specifications

Following the **Codebase Design (Deep Modules)** philosophy, complex logic is encapsulated behind minimal, robust seams:

### 4.1 Search Engine Seam (`scripts/template/search-template.py`)

- **Interface**: `search_templates(role, style=None, target_pages=1, density="balanced", keywords=None, engine="hybrid") -> List[Dict]`
- **Implementation**: Pluggable `BaseTemplateScorer` hierarchy (`WeightedRuleScorer`, `BM25TextScorer`, `HybridTemplateScorer`).
- **Leverage**: Callers pass high-level query parameters; tokenization, BM25 TF-IDF computation, and multi-criteria scoring are fully hidden behind the seam.

### 4.2 Workspace Canvas Instantiator Seam (`scripts/template/instantiate-resume.py`)

- **Interface**: `instantiate_workspace(template_id, profile_path=None, keywords=None, output_path="workspace/resume.html", quiet=False, font_preset="system") -> Path`
- **Implementation**: Resolve `canvas.html`, validate named slot counts and contexts, normalize the explicit profile with `scripts/contracts/profile.py`, escape supplied text, and bind once. Inline CSS in order: `common/base.css`, template `style.css`, `common/canvas-bindings.css`, then an optional font preset. Publish HTML atomically after complete assembly.
- **Invariants**: Each template maintains exactly one HTML structure, `canvas.html`. `sample-profile.json` is explicitly fictional gallery input, never a fallback for absent user facts. `build-gallery.py` uses the same instantiator and CSS to generate previews under `output/templates_gallery/`. Invalid or missing samples fail the build before preview publication.
- **Output**: Generated HTML embeds its styles and has no external network asset requirement. Font availability still matters: the explicit `arial-unicode` preset requires a matching local face and must not silently pass font QA when unavailable. The pipeline always passes an isolated output path; the function default remains a standalone convenience.

### 4.3 Profile & Run Orchestration Seam

- **Contract**: `scripts/contracts/profile.py` and `src/knowledge/resume-schema.json` define normalization shared across Draft, Master and Variant. Raw legacy profile JSON remains accepted as explicit Master input; wrapped documents carry lifecycle and provenance.
- **Orchestration**: `scripts/pipeline/forge.py` snapshots input, creates the isolated run, binds the Variant, checks QA protocol/status consistency and accepted-file hashes, then records delivery in the manifest.
- **Publication**: Requested output copies are staged only after acceptance. Ordinary copy failures roll back, and destination locks prevent tool processes from interleaving copies. Cross-file publication is not a crash-safe filesystem transaction; canonical run artifacts and the manifest remain authoritative.

### 4.4 Rendering & Acceptance Seam

- **Implementation**: `scripts/rendering/browser-engine.js` is shared by Python and TypeScript validation/rendering entry points. It uses print media, waits for fonts/resources, checks all page containers and clipping, generates fresh PDF bytes, and validates A4 geometry, page count and per-page text coverage before publishing those exact bytes.
- **Failure semantics**: Unavailable runtime or invalid checking protocol returns `UNVERIFIED`; estimates cannot substitute for measured acceptance. Failed operations do not replace an existing accepted PDF with incomplete output.
- **Pagination**: Each explicit `.resume-page` maps to one A4 page. `--expected-pages` is a maximum of one or two pages; two-page layouts need two containers. Implicit overflow from a single oversized root is rejected.
- **Review boundary**: Automated text checks establish basic text availability and coverage, not universal ATS compatibility, factual truth or visual quality. Agent review remains necessary.

---

## 5. Two-Tier Design Tokens Architecture

To enable instant theme inheritance, zero code duplication, and deterministic agent self-healing, CSS variables are organized into two layers:

```css
/* === Layer 1: Primitive Tokens (common/base.css) === */
:root {
  --primitive-color-slate-900: #0f172a;
  --primitive-color-blue-600:  #2563eb;
  --primitive-space-1: 2pt;
  --primitive-space-2: 4pt;
  --primitive-space-4: 8pt;
  --primitive-space-6: 12pt;
  --primitive-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
  --primitive-page-width: 210mm;
  --primitive-page-min-height: 297mm;
}

/* === Layer 2: Component Tokens (template style.css) === */
:root {
  --resume-color-primary: var(--primitive-color-slate-900);
  --resume-color-accent: var(--primitive-color-blue-600);
  --resume-space-section: var(--primitive-space-6);
  --resume-space-item: var(--primitive-space-4);
  --resume-font-size-body: var(--primitive-font-size-body);
}
```

---

Shared `canvas-bindings.css` connects generated components to this token system. Adjust supported component tokens rather than duplicating template structure or adding arbitrary inline body styles. The metadata and actual CSS define supported tuning controls.

Automatic healing stages changes and commits them only after acceptance. It must not increase the current spacing, reduce body text below 8.8pt, or rewrite facts to fit. Failed tuning leaves the original canvas intact. Local font-preset choice belongs in Variant provenance separately from candidate facts.

## 6. Architecture Decision Records (ADRs)

Key architectural choices are formally documented in `docs/decisions/`. ADRs record design rationale; historical implementation examples are subject to the current artifact and browser-acceptance contracts:

1. [ADR-0001: HTML as Sole Intermediate Working Canvas](docs/decisions/0001-html-intermediate-canvas.md)
2. [ADR-0002: Pure CSS3 Design Tokens over Tailwind Runtime](docs/decisions/0002-pure-css-design-tokens-over-tailwind.md)
3. [ADR-0003: Two-Tier Token Architecture (Primitives + Components)](docs/decisions/0003-two-tier-tokens-architecture.md)
4. [ADR-0004: Decentralized JSON Metadata with Build-Time BM25 Index](docs/decisions/0004-decentralized-json-with-bm25-index.md)
5. [ADR-0005: Heuristic Design Token Auto-Healing for Page-Fit Closed Loop](docs/decisions/0005-heuristic-token-auto-healing.md)
6. [ADR-0006: Lightweight Zero-Dependency Live Preview & Conversational Intake Wizard](docs/decisions/0006-zero-dependency-live-preview-and-wizard.md)

---

## 7. Product & Engineering Iteration Roadmap

Detailed iteration specifications and roadmap tasks are governed in:

- [v0.0.6 Iteration Plan & Engineering Specification](docs/dev/ITERATION_PLAN_V0.0.6_EXPERIENCE_EXPANSION.md)


### Current implementation and verification

The current implementation includes shared profile/error contracts, isolated runs, complete slot binding, single-source template structures, print-media measurement of every page, and final PDF acceptance. User conversation and supplied information remain the input path; repository mining is not an implemented resume-generation capability.

Tests use temporary directories and cover sparse/invalid facts, multiple education entries, injection errors, sample isolation, gallery/direct output equality, concurrent runs, missing runtime, all-page layout/PDF checks and preservation of old outputs. Keep these safeguards as regression checks when extending the roadmap. Refer to the linked iteration plan for proposed work rather than inferring completion from this architecture diagram.


### Agent Skills package boundary

`SKILL.md` is the portable Agent Skills entry; `skill.json` and platform configuration files are project/client extensions. The repository name differs from the Skill identifier: stage or install as `knowme-careerforge` for name-directory validation. `src/templates/` and `src/knowledge/` remain valid resource locations; the format does not require an `assets/` migration.

Discovery metadata, activated instructions and conditional resources have separate loading costs. Keep development governance in `AGENT.md` and detailed runtime rules in `references/`. Package verification must cover dependencies and execution from outside the source checkout, separately from source-tree tests and Agent behavior evaluation.

The current initializer has unresolved packaging and partial-success gaps; native-platform compatibility is not established by copying a prompt or passing local PDF tests. See [Agent Skills design review](docs/dev/AGENT_SKILLS_DESIGN_REVIEW.md) for evidence, target boundaries and acceptance criteria, and `AGENT.md` section 7 for maintenance rules.
