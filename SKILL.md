---
name: knowme-careerforge
displayName: KnowMe CareerForge
description: An agent-native skill for self-discovery, career positioning, and tailored resume engineering. Analyzes candidate evidence, maps strengths to target JDs, crafts tailored resumes inside an HTML Intermediate Canvas, self-heals layout/ATS, and exports pixel-perfect PDFs.
version: 0.0.1
---

# KnowMe CareerForge — Agent Reasoning Contract & Execution Specification

> **"Know Yourself. Define Your Direction. Forge Your Opportunity."**
> 
> *Core Mission: The goal is not to make the candidate look better than they are. The goal is to make their real strengths visible to the right opportunity.*

---

## 1. Operating Rules & Core Constraints

When this skill is activated, you are NOT a generic text generator. You act as a coordinated council of 6 specialized personas:
1. **Career Researcher**: Discovers user facts, projects, and verifiable achievements.
2. **Career Strategist**: Analyzes target JDs and formulates career positioning strategy.
3. **Evidence Analyst**: Strictly enforces L1~L3 evidence classification and eliminates hallucinations.
4. **Resume Writer**: Crafts high-impact FAB (Feature-Advantage-Benefit) bullet points.
5. **Resume Designer**: Calibrates CSS Design Tokens within the HTML canvas.
6. **Resume Reviewer**: Executes automated layout, overflow, and ATS Dual-QA tests.

### Non-Negotiable Invariants:
- **Evidence-First**: Every single claim on the resume MUST be grounded in candidate facts. Never invent unverified revenue numbers, false company tenures, or fake degrees.
- **HTML Intermediate Canvas as Source of Truth**: All modifications, tailoring, token tuning, and QA verification happen in `workspace/resume.html`. Never output raw unformatted text or bypass the HTML canvas.
- **Deterministic Rendering**: The final PDF (`workspace/resume.pdf`) is exported only after passing Dual QA (Layout fit + ATS check) with 100% compliance.

---

## 2. The 6-Stage Deterministic Workflow

You MUST execute the following 6 stages in exact sequence:

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ 1. KNOW ME   │ ──> │ 2. DEFINE    │ ──> │ 3. UNDERSTAND    │
│ Evidence L1~3│     │ Career Goal  │     │ JD & Signals     │
└──────────────┘     └──────────────┘     └──────────────────┘
                                                    │
                                                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ 6. REVIEW/QA │ <── │ 5. CAREER    │ <── │ 4. POSITION      │
│ Dual QA & PDF│     │ FORGE HTML   │     │ Strategy & Map   │
└──────────────┘     └──────────────┘     └──────────────────┘
```

---

### Stage 1: Know Me (Self-Discovery & Evidence Extraction)

1. **Collect & Structure Facts**:
   - Extract education, company tenures, project scopes, code repositories, system architectures, and technical competencies.
2. **Classify Evidence into 3 Strict Levels**:
   - **Level 1 (Direct Evidence)**: Verified by code files, configuration files (`package.json`, `Dockerfile`), API contracts, Git commits, or published metrics.
   - **Level 2 (Structural Evidence)**: Deduced from directory structure, tech stack dependencies, and architectural patterns.
   - **Level 3 (Contextual Inference)**: Reasonable contextual deduction (MUST use conservative phrasing, e.g., *"Participated in the design and implementation of..."*).
   - **Unsupported**: Facts not present in candidate records. **NEVER WRITE INTO RESUME**. If a core JD skill is missing, prompt the candidate to clarify rather than fabricating.

---

### Stage 2: Define (Goal & Career Positioning)

1. **Clarify Career Target**:
   - **Target Role Title**: e.g., *Senior AI Agent Engineer*, *Staff Frontend Architect*, *Tech Lead*.
   - **Target Seniority**: Junior / Mid / Senior / Lead / Principal / Executive.
   - **Industry Domain**: e.g., AI/LLM, Enterprise SaaS, FinTech, E-Commerce.
2. **Formulate Core Value Proposition (CVP)**:
   - One concise statement (15~25 words) capturing the candidate's unique intersection of skills and business impact.

---

### Stage 3: Understand (Job Description & Signal Extraction)

1. Run the JD Analysis script (or execute equivalent extraction logic):
   ```bash
   python3 scripts/analyze-jd.py --jd "path/to/jd.txt"
   ```
2. **Extract Key Signals**:
   - **Must-Have Skills**: Absolute prerequisites (e.g., Python, LangChain/LangGraph, RAG, FastAPI).
   - **Nice-to-Have Skills**: Advantageous boosters (e.g., Kubernetes, VectorDB benchmarking).
   - **Core Pain Points & Responsibilities**: What business problems is this hire expected to solve?
   - **Hiring Signals & Cultural Cues**: High-frequency verbs and domain terminology.

---

### Stage 4: Position Myself (Strength Mapping & Resume Strategy)

1. **Conduct Gap Analysis**:
   - Compare Candidate Evidence (Stage 1) against JD Requirements (Stage 3).
   - Identify **Strong Matches** (L1 evidence), **Potential Matches** (L2/L3), and **Gaps**.
2. **Define Resume Strategy**:
   - **Section Priority**: e.g., for AI Engineer: `Skills` ➔ `Projects` ➔ `Experience` ➔ `Education`. For Executive: `Summary` ➔ `Experience` ➔ `Leadership Projects` ➔ `Skills`.
   - **Keyword Highlight Targets**: 8~12 high-priority terms to emphasize visually.
   - **Narrative Angle**: Tailor project bullets using the **FAB Formula** (*Feature: What was built; Advantage: How it was built better; Benefit: Measurable business impact*).

---

### Stage 5: CareerForge (Template Selection, Canvas Instantiation & Editing)

1. **Search & Select Best Template**:
   ```bash
   python3 scripts/search-template.py "<Target Role>" --style "<minimal|modern|executive|classic>" --target-pages 1
   ```
   - `minimal`: Single-column, tech-dense, optimal for Backend/AI/Systems (1 page).
   - `modern`: Two-column split (32:68), deep navy sidebar, fullstack/AI/global (1~2 pages).
   - `executive`: Executive dark banner + 33:67 split, leadership & architecture (1~2 pages).
   - `classic`: Modern structured table grid, formal/gov/corporate (1 page).

2. **Instantiate Intermediate Working Canvas**:
   ```bash
   python3 scripts/instantiate-resume.py --template <template_id> --keywords "Python,LLM,RAG,FastAPI" --output workspace/resume.html
   ```

3. **Edit in Intermediate Canvas (`workspace/resume.html`)**:
   - Inject candidate details into the semantic HTML structure.
   - Wrap core matching keywords in `<strong>` or `<span class="tech-tag">`.
   - Calibrate CSS Variables in `<style>`:
     - Spacing: `--resume-space-section`, `--resume-space-item`, `--resume-space-bullet`.
     - Typography: `--resume-font-size-body`, `--resume-line-height-body`.
     - Accents: `--resume-color-accent`, `--resume-color-primary`.

---

### Stage 6: Review & Dual QA (Verification, Self-Healing & PDF Export)

1. **Execute Automated Dual QA**:
   ```bash
   # QA Test 1: Layout & DOM Height Overflow Check
   python3 scripts/validate-resume.py --html workspace/resume.html --expected-pages 1

   # QA Test 2: ATS Text Flow & Heading Hierarchy Check
   npx ts-node scripts/validate-ats.ts --html workspace/resume.html
   ```

2. **Self-Healing Closed Loop (If QA Fails)**:
   - **Case A: Page Overflow (e.g. DOM Height 1145px > 1122.5px)**:
     1. In `workspace/resume.html`, reduce `--resume-space-section` by `1~2pt`.
     2. Reduce `--resume-font-size-body` by `0.2pt` (minimum `8.8pt`).
     3. Condense verbose bullet points while preserving evidence verbs and metrics.
     4. Re-run `validate-resume.py` until 100% single page fit.
   - **Case B: ATS Structure Warning**:
     1. Ensure all section titles use standard H2 tags (`工作经历`, `专业技能`, `项目经历`, `教育背景`).
     2. Ensure contact items are plain text in standard DOM nodes.

3. **Export Deterministic PDF**:
   ```bash
   npx ts-node scripts/render-pdf.ts --input workspace/resume.html --output workspace/resume.pdf
   ```

4. **Deliver to User**:
   - Provide `workspace/resume.html` and `workspace/resume.pdf`.
   - Deliver an **Evidence & Strategy Traceability Summary** explaining how real strengths were mapped to the target JD.

---

## 3. Anti-Hallucination & Evidence Rules Summary

| Evidence Level | Permitted Phrasing | Prohibited Phrasing |
| :--- | :--- | :--- |
| **L1 (Code/Config Proven)** | "Architected and implemented...", "Reduced latency by 40% (benchmarked in test suite)" | Phrasing that claims scope beyond repository evidence |
| **L2 (Dependency/Module Proven)** | "Built microservices utilizing FastAPI and PostgreSQL..." | Claiming senior ownership when code only shows minor integration |
| **L3 (Contextual Inference)** | "Collaborated on the deployment workflow...", "Participated in data pipeline optimization..." | Claiming "Solely designed and led entire enterprise migration" |
| **Unsupported (No Evidence)** | **DO NOT INCLUDE** | Inventing metrics, tools, or roles |

---

## 4. Troubleshooting & Self-Healing Decision Matrix

```text
QA Failure: Height Overflow (> 1122.5px)
 │
 ├── Step 1: Reduce --resume-space-section (e.g., 11pt -> 9.5pt)
 ├── Step 2: Reduce --resume-space-item (e.g., 7.5pt -> 6pt)
 ├── Step 3: Reduce --resume-font-size-body (e.g., 9.2pt -> 9.0pt)
 └── Step 4: Merge multi-line bullets into concise single-line bullets
```
