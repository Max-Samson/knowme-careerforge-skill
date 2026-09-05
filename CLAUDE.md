# KnowMe CareerForge project guidance

Read SKILL.md for the user-input workflow and references/07-artifact-contract.md for Draft/Master/Variant, missing values, isolated run directories and PASS/FAIL/UNVERIFIED semantics.

User information and explicitly supplied resume material are the input. Do not scan the repository to manufacture career facts. Prepare a profile internally; the user need not write JSON. Use `forge --profile-json <file>` for an isolated run and `--draft` for incomplete drafts. Never identify delivery by an old workspace/resume.pdf.

During development run `npm test` after installing dependencies. Tests must keep generated candidate data and PDFs in temporary directories. Validation and rendering must share browser-engine.js and check actual print output and final PDF text. Never introduce fallback estimates that return PASS or swallow binding/render failures.
