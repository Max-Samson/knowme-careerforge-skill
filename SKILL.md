---
name: knowme-careerforge
description: Create or refine a tailored resume from user descriptions, existing resume material and an optional target JD. Use when the user wants to draft a resume, tailor it to a role, edit an existing resume canvas, or export a verified resume PDF.
license: MIT
compatibility: Requires Python 3.9+, Node.js 22.13+, the npm dependencies declared by this project, and Chromium for print/PDF checks. Explicit local font presets require the named font.
metadata:
  version: 0.0.5
---

# KnowMe CareerForge

Use the user's descriptions, existing resume and supplied supporting material. The host Agent understands, selects and rewrites content. Repository mining and automatic repo-to-resume backfill are not supported input paths. Do not scan the current project to infer candidate facts.

Reuse information already given and ask only useful follow-up questions. A target role is enough; a JD is optional. Make progress with sparse information when the user wants a draft. Do not impose a complete questionnaire or invent facts to fill empty fields. Preserve explicit user choices of language, template, page count and requested edit.

Keep employers, dates, degrees, responsibilities, metrics and ownership faithful to the input. User statements are supplied facts; do not downgrade “led” to “participated” merely because the source is chat. Do not claim independent verification without doing it. Keep gaps and uncertainties outside the resume rather than writing invented placeholder achievements.

For help developing or reviewing this Skill repository, use its development documentation; do not start a candidate intake or resume-generation workflow merely because the repository contains resume tools.

## Preserve the artifact lifecycle

Read [the shared artifact and error contract](references/07-artifact-contract.md) before running the pipeline. Draft, Master and Variant describe different artifacts. They do not mean the same thing as PASS, FAIL or UNVERIFIED.

- Prepare a Draft when information is incomplete. Unknown optional values are omitted or null, never sample candidate text.
- Keep the user's facts in a Master; derive a Variant for a target role without overwriting the original facts. User-provided plain profile JSON remains supported. Users do not need to author JSON themselves.
- Use an isolated run directory for each pipeline invocation. Read the returned manifest and exact output paths; never infer success from an existing workspace/resume.pdf.
- When editing an existing canvas, preserve those edits and validate/render that canvas. Do not regenerate from an older profile and overwrite later content edits. Write a new output path for a new revision.

Resolve scripts and resources relative to this SKILL.md, regardless of current directory. Write candidate artifacts in the user's workspace. Tools require Python 3.9+, Node.js 22.13+ and installed npm runtime dependencies. Printing requires system Chromium or Playwright Chromium. Missing runtime means UNVERIFIED, not PASS.

```bash
# Assemble and verify Agent-prepared user facts in an isolated run directory.
python3 <skill-root>/scripts/pipeline/forge.py --profile-json <master.json> --role "<target role>" --template minimal --quiet

# Incomplete input: return a draft, without a verified PDF claim.
python3 <skill-root>/scripts/pipeline/forge.py --profile-json <draft.json> --draft --quiet

# Validate an existing edited canvas; export rechecks the final PDF.
python3 <skill-root>/scripts/validation/validate-resume.py <resume.html> --expected-pages 1 --json
python3 <skill-root>/scripts/rendering/render-pdf.py <resume.html> <new-resume.pdf> --expected-pages 1 --quiet
```

## Assemble and inspect

Use `canvas.html` as the sole maintained template structure. Gallery previews bind explicit `sample-profile.json` through the same instantiator; never use gallery samples as candidate facts. All education, work and project entries are independent. Treat an injection error as failure; never deliver the untouched sample template. For template choice and token tuning, read [template guidance](references/04-template-selection.md) and [canvas guidance](references/05-html-canvas-tokens.md).

Check facts against the input, inspect print layout and run [QA and rendering](references/06-qa-and-rendering.md). Automatic tuning may reduce spacing and font sizes within limits, but cannot replace content review. When fitting fails, adjust expression, select another layout or use the user's allowed page count. Do not silently delete facts. If PDF extraction reports font mapping differences, inspect missingCodepoints and extractedRadicals; an explicit available font preset such as `--font-preset arial-unicode` can be used in a new run. Never relax text checks or rewrite candidate facts to bypass a font failure.

Report the actual result concisely with the produced file paths. PASS requires the current PDF's page, text and layout checks. FAIL or UNVERIFIED must explain the concrete error; DRAFT must be labeled as a draft. Basic PDF text checks are not universal ATS certification.
