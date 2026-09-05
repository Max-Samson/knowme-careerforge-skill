# Script responsibilities

- contracts/: shared Draft/Master/Variant normalization and missing-value rules.
- pipeline/: unique run directory, immutable input snapshot, Master and Variant lineage, explicit result manifest and verified copies.
- evidence/: optional JD helpers; legacy extract-evidence.py is not a supported candidate input path.
- template/: template ranking and deterministic fact-only canvas binding.
- validation/: print-mode geometry and content checks through the shared browser engine; no estimate-based PASS.
- rendering/: final PDF page/text validation and atomic write, preserving old outputs on failure.
- build/: package, gallery and test utilities. Tests must write only to temporary directories.

Read ../references/07-artifact-contract.md for the authoritative artifact lifecycle, status/exit-code rules and output contract. Runtime scripts are resolved from the Skill installation; candidate artifacts belong to the user's workspace. A Draft is useful output but is never a verified PDF. FAIL and UNVERIFIED are nonzero exits in JSON and human-readable modes.
