---
name: knowme-careerforge
description: Draft, expand or refine high-quality resume content from user descriptions, existing resume material and an optional target JD. Use when the user wants to draft a resume, tailor it to a role, edit an existing resume canvas, or export a verified resume PDF.
license: MIT
compatibility: Content drafting needs only the host Agent. PDF export requires Python 3.9+, Node.js 22.13+, the npm dependencies declared by this project, and Chromium for print/PDF checks. Explicit local font presets require the named font.
metadata:
  version: 0.0.7
---

# KnowMe CareerForge

Create a readable resume from the user's descriptions, existing resume and explicitly supplied material. The host Agent discovers relevant strengths, expands terse experience into concrete professional writing, and selects evidence for the target role. Role and writing templates guide its reasoning; tools only bind templates and check printing. Content-only drafting and editing are complete deliverables when requested; they do not require JSON, a runtime check or PDF generation. Repository mining and automatic repo-to-resume backfill are not supported. Development tasks use AGENT.md; making a resume does not require reading development docs or tool source code.

## 1. Start from the conversation

Reuse information already given. A target role is sufficient to start the conversation, not to invent a candidate. A JD is optional. Decide whether candidate material exists before reading references, inspecting templates or checking runtime. With no material, a sufficient first response is: “请发已有简历，或告诉我姓名、最近一段工作经历（公司、时间、做了什么、用过哪些技术）；已有的信息不用重复。”

- **Only a role, no candidate material:** ask for an existing resume or a short description of recent work, dates and technologies. Then wait. Do not build sample resumes, inspect every reference, or create test profiles while awaiting an answer. If a host task list is used, mark intake as awaiting input using the host’s supported state; drafting and rendering depend on it and remain pending. A TODO reminder does not unlock them. Do not create a task list just to run this simple workflow.
- **Usable facts supplied:** organize them directly. Missing optional contact, school or date fields do not require a Draft detour. Ask only consequential follow-ups; proceed with known facts when the user wants a result. A missing name does not block content writing. For PDF delivery, ask just for the required name, or prepare an unnamed Draft if requested.
- **Draft requested or delivery input insufficient:** use `--draft` for an explicitly requested partial canvas. Label it DRAFT; do not promise a verified PDF.
- **Existing canvas edited:** stage those edits in memory and validate/render them to the current delivery paths; create a separate revision only when requested. Do not rebuild from an older profile.

Preserve employers, dates, qualifications, metrics and ownership exactly in meaning. “Participated” cannot become “led”; a target Java role does not prove Java experience. Role knowledge and JD keywords are prompts for questions, never evidence of skills. Do not add common tools, proficiency, implementation mechanisms, projects or outcomes merely because they sound plausible. Gallery `sample-profile.json` is fictional and never candidate input. If a user explicitly requests a fictional example, label it separately and keep it out of their fact record.

## 2. Develop the content, then choose its presentation

Before drafting or materially expanding content, read [source-grounded expansion](references/01-evidence-mining.md). Turn raw descriptions into useful resume evidence, not merely shorter paraphrases. Expand the supplied action, object, context and technical relationship; make supported abilities visible. A role template supplies writing angles and questions, not a candidate history. Keep unsupported suggestions out of the final resume.

Route only to the guidance needed:

- **Terse experience or a request to expand:** use the expansion patterns and examples in reference 01. Ask the highest-value missing question when it would change the core claim; otherwise produce a useful version immediately.
- **Positioning, career transition or ability-focused writing:** read [career positioning](references/02-career-goal.md) and, when useful, the one relevant `src/knowledge/roles/*.json`. Infer transferable abilities from actual actions without inventing proficiency or tools.
- **A supplied JD or role-tailoring request:** read [JD alignment](references/03-jd-analysis.md). Map requirements to direct evidence, transferable evidence and gaps; select and order content accordingly. The JD parser is optional and does not perform this reasoning.
- **Contact-only or other narrow edits:** change the requested fields; do not restart positioning or expand unrelated content.

Keep a lightweight content plan in context: target role, strongest supported abilities, supporting experiences, and consequential gaps. This is reasoning support, not a required report, questionnaire or approval step. Follow the user's preference for immediate drafting versus deeper exploration.

Choose content by relevance, specificity, personal contribution and distinctiveness. Expand strong but terse evidence; compress repetitive or low-relevance material. Preserve meaningful career context and chronology. Selecting facts for a tailored resume is permitted; changing their meaning or deleting important content just to pass layout checks is not. Explain a material omission briefly when needed. A summary should synthesize supported strengths, work entries should demonstrate them, and projects should add distinct evidence rather than duplicate work.

Review content before formatting: can a reader identify the target, the candidate's contribution and the strongest supporting evidence? Use the editorial review in reference 01 to remove empty expansion, unsupported causal claims and repeated achievements; do not force sparse inputs into a full resume structure. Replace generic praise with concrete supplied actions; preserve outcomes without numbers when that is all the source supports. Compare claims with the original user material, not just the generated profile. If a request is content-only, return the polished text and any consequential open question here. Do not force a PDF workflow.

For HTML/PDF delivery, prepare the selected, rewritten profile in memory and read [the artifact contract](references/07-artifact-contract.md). The pipeline's Master is the supplied run snapshot, not a complete lifetime fact bank; Variant does not automatically tailor the prose. Keep original user material as the factual reference in context. Do not create permanent profiles or analysis files unless requested.

Read [template guidance](references/04-template-selection.md) when choosing a layout. Content priorities come first: choose for actual length, section hierarchy and user preference. Honor an explicit template choice. The default template order is not a mandatory editorial order; adapt the canvas when a substantive request needs a different hierarchy, then validate it. For content that warrants two pages, explicitly compose two page containers and use `--expected-pages 2`; this flag alone does not paginate a template. State the actual `templateUsed` in PDF delivery.

## 3. Generate only when a file deliverable is needed

For HTML/PDF requests, read [production commands and QA](references/06-qa-and-rendering.md) before the first build or canvas update. It contains runtime preparation, stdin commands, safe update handling and diagnostics. Use the host-resolved skill root and the user's output workspace. Default production leaves only the current HTML/PDF pair; archives are opt-in. Never overwrite the current canvas before validation or treat an old PDF as this run's result.

For content-only requests, deliver copy-ready prose in the requested language and scope. A single bullet edit needs only that bullet; a complete resume needs coherent sections. Keep suggestions or unresolved questions outside the resume body. Do not append a mandatory questionnaire, editing report, capability score or disclaimer to otherwise usable content.

## 4. Inspect and deliver

Check rewritten content against the user's input before rendering. After tool acceptance, inspect the final PDF visually on every page: hierarchy, small type, excessive whitespace, dense skills, duplication and education/date alignment. Keep any inspection images and helper scripts in a system temporary directory; remove only these self-created temporary files after inspection, including failed inspection attempts. Do not save them beside the resume unless requested. An HTML screenshot or PDF file size does not prove final PDF appearance. If visual tools are unavailable, disclose that limitation. After an accepted result and the completed visual/content review, stop. Do not perform another identical export, measure file size as extra QA, or create another named copy. Read [canvas tuning](references/05-html-canvas-tokens.md) only for layout edits and [QA diagnostics](references/06-qa-and-rendering.md) for failures.

PASS requires this PDF's page, text and layout checks. It does not certify truth, persuasive design or universal ATS compatibility. Do not shrink sparse resumes, fabricate content to fill the page, silently remove facts, or relax checks to pass. Use returned failure diagnostics; retain full run files only through explicit diagnostic mode. Do not delete user-owned files or old archives as cosmetic cleanup. Font extraction failures require inspecting diagnostics and an available font choice, not altering candidate text.

Default HTML/PDF delivery: link PDF and editable HTML, name the template, and briefly note useful remaining gaps. Do not repeat the entire resume, dump QA tables, or link input/Master/Variant/manifest unless requested or needed to explain failure. FAIL/UNVERIFIED must identify the concrete blocker; DRAFT must remain clearly labeled.

For an HTML/PDF request, use one concise delivery shape across hosts, adapting only language and filenames:

> 已生成简历： [PDF](<current PDF path>) · [可编辑 HTML](<current HTML path>)。模板：<templateUsed>。<One useful gap or actual inspection limitation, if any.>

Return one current version by default, not several template alternatives or separate analysis reports. For an update, patch only the requested fields in the current working profile/canvas, retain the selected template and public filenames unless the user asks to change them, and publish the newly accepted revision; leave existing archives untouched and let the pipeline clean its temporary staging. When blocked, give the blocker and the single next action instead of a success-shaped delivery. Keep progress updates about observable work, not a running commentary of every file read or schema decision.
