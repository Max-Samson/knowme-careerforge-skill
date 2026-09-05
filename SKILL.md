---
name: knowme-careerforge
description: Create or refine a tailored resume from user descriptions, existing resume material and an optional target JD. Use when the user wants to draft a resume, tailor it to a role, edit an existing resume canvas, or export a verified resume PDF.
license: MIT
compatibility: Requires Python 3.9+, Node.js 22.13+, the npm dependencies declared by this project, and Chromium for print/PDF checks. Explicit local font presets require the named font.
metadata:
  version: 0.0.6
---

# KnowMe CareerForge

Create a readable resume from the user's descriptions, existing resume and explicitly supplied material. The host Agent selects and rewrites facts; tools bind templates and check printing. Repository mining and automatic repo-to-resume backfill are not supported. Development tasks use AGENT.md; making a resume does not require reading development docs or tool source code.

## 1. Start from the conversation

Reuse information already given. A target role is sufficient to start the conversation, not to invent a candidate. A JD is optional. Decide whether candidate material exists before reading references, inspecting templates or checking runtime. With no material, a sufficient first response is: “请发已有简历，或告诉我姓名、最近一段工作经历（公司、时间、做了什么、用过哪些技术）；已有的信息不用重复。”

- **Only a role, no candidate material:** ask for an existing resume or a short description of recent work, dates and technologies. Then wait. Do not build sample resumes, inspect every reference, or create test profiles while awaiting an answer. If a host task list is used, mark intake as awaiting input using the host’s supported state; drafting and rendering depend on it and remain pending. A TODO reminder does not unlock them. Do not create a task list just to run this simple workflow.
- **Usable facts supplied:** organize them directly. Missing optional contact, school or date fields do not require a Draft detour. Ask only consequential follow-ups; proceed with known facts when the user wants a result. If experience is known but the name is missing, ask just for the name needed for PDF delivery, or prepare an unnamed Draft if requested.
- **Draft requested or delivery input insufficient:** use `--draft` for an explicitly requested partial canvas. Label it DRAFT; do not promise a verified PDF.
- **Existing canvas edited:** preserve those edits and validate/render that canvas to a new revision path; do not overwrite it from an older profile.

Preserve employers, dates, qualifications, metrics and ownership exactly in meaning. “Participated” cannot become “led”; a target Java role does not prove Java experience. Role knowledge and JD keywords are prompts for questions, never evidence of skills. Do not add common tools, proficiency, implementation mechanisms, projects or outcomes merely because they sound plausible. Gallery `sample-profile.json` is fictional and never candidate input. If a user explicitly requests a fictional example, label it separately and keep it out of their fact record.

## 2. Compose once, choose a layout

Before composing, read [the source-to-claim rules](references/01-evidence-mining.md) once and check the rewritten claims against the original user material. Comparing a generated profile with its own PDF does not check factual fidelity. Keep a single editable profile of supplied facts. Read [the artifact contract](references/07-artifact-contract.md) for its short input example and lifecycle. The pipeline creates Master/Variant snapshots; the user need not write JSON or receive every snapshot. Master means this run's known facts, not that every optional field is complete.

Write short, concrete bullets. A useful default is a brief optional summary, compact skill groups, and evidence in work/project entries. Do not repeat the same achievement in summary, work and an invented project. A project section is optional: add one only when supplied project detail adds something distinct. Metrics and technical mechanisms appear only when supplied; duties without metrics remain valid. Follow the user's requested level of detail.

Read [template guidance](references/04-template-selection.md) when choosing a template. Honor an explicit choice; otherwise choose for actual content length and hierarchy, or omit `--template` for ranked selection. Do not hardcode minimal because the role is backend. State the actual `templateUsed` in delivery. Each template has one structural source, `canvas.html`; previews bind fictional data through the same renderer.

## 3. Prepare runtime, generate

Use the absolute SKILL.md path already returned by the host to resolve `<skill-root>`. The model name does not determine the installation directory: a Gemini model may be running through a host that resolves `.claude/skills`. If unavailable, inspect the host's configured skill location; do not recursively search the home directory. Candidate files belong in the user's workspace, never the installation directory.

After there is sufficient candidate material, and before the first PDF build, run:

```bash
node <skill-root>/scripts/rendering/browser-engine.js --check-runtime
```

READY only checks runtime availability, not resume quality. If unavailable, use its diagnostics and the installed package.json to prepare dependencies once under the host's permission rules. With a lockfile use `npm ci --omit=dev`; otherwise use `npm install --omit=dev`, in `<skill-root>`. Do not guess and install packages one error at a time. If package.json or required bundled scripts are absent, the installation is incomplete: repair it from the project package rather than synthesizing a manifest or installing guessed dependencies. Chromium is also required. If setup is blocked, report UNVERIFIED and offer a requested Draft; do not repeatedly run the full pipeline unchanged.

For a new resume, keep internal files under `workspace/` and publish only the readable deliverables under `resume/` (or the user's chosen locations):

```bash
python3 <skill-root>/scripts/pipeline/forge.py --profile-json workspace/profile.json --workspace workspace/runs --role "<target role>" --output resume/resume.pdf --html-output resume/resume.html --summary
```

Add `--template <chosen-id>` for an explicit layout. Drafts use `--draft` without PDF/copy flags; return the exact HTML path reported. Each invocation isolates its artifacts. A successful preflight need not be repeated on contact or wording updates unless the environment changes. Read the returned status and paths; never guess `workspace/resume.pdf` or treat a previous copy as this run's success. Full diagnostics remain in the returned manifest; open them only when needed. Fix a reported cause before retrying.

For existing edited HTML:

```bash
python3 <skill-root>/scripts/rendering/render-pdf.py <edited-resume.html> <new-resume.pdf> --expected-pages 1 --quiet
```

## 4. Inspect and deliver

Check rewritten content against the user's input before rendering. After tool acceptance, inspect the final PDF visually on every page: hierarchy, small type, excessive whitespace, dense skills, duplication and education/date alignment. An HTML screenshot or PDF file size does not prove final PDF appearance. If visual tools are unavailable, disclose that limitation. After an accepted result and the completed visual/content review, stop. Do not perform another identical export, measure file size as extra QA, or create another named copy. Read [canvas tuning](references/05-html-canvas-tokens.md) only for layout edits and [QA diagnostics](references/06-qa-and-rendering.md) for failures.

PASS requires this PDF's page, text and layout checks. It does not certify truth, persuasive design or universal ATS compatibility. Do not shrink sparse resumes, fabricate content to fill the page, silently remove facts, or relax checks to pass. Preserve failures for diagnosis; do not delete run history as cosmetic cleanup. Font extraction failures require inspecting diagnostics and an available font choice, not altering candidate text.

Default delivery: link PDF and editable HTML, name the template, and briefly note useful remaining gaps. Do not repeat the entire resume, dump QA tables, or link input/Master/Variant/manifest unless requested or needed to explain failure. FAIL/UNVERIFIED must identify the concrete blocker; DRAFT must remain clearly labeled.

Use one concise delivery shape across hosts, adapting only language and filenames:

> 已生成简历： [PDF](<current PDF path>) · [可编辑 HTML](<current HTML path>)。模板：<templateUsed>。<One useful gap or actual inspection limitation, if any.>

Return one current version by default, not several template alternatives or separate analysis reports. For an update, patch only the requested fields in the current working profile/canvas, retain the selected template and public filenames unless the user asks to change them, and publish the newly accepted revision; keep previous runs internal. When blocked, give the blocker and the single next action instead of a success-shaped delivery. Keep progress updates about observable work, not a running commentary of every file read or schema decision.
