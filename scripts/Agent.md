# Script responsibilities

- contracts/: shared Draft/Master/Variant normalization and missing-value rules.
- pipeline/: isolated temporary staging by default, explicit retained archives, immutable input snapshots, Master/Variant lineage, and atomic verified delivery pairs.
- evidence/: optional JD helpers; legacy extract-evidence.py is a fail-only compatibility entry shared by CLI/npm/direct callers; it must not read repositories or write candidate profiles.
- template/: template ranking and deterministic fact-only canvas binding.
- validation/: print-mode geometry and content checks through the shared browser engine; no estimate-based PASS.
- rendering/: final PDF page/text validation and atomic write, preserving old outputs on failure.
- build/: package, gallery and test utilities. Tests must write only to temporary directories.

Read ../references/07-artifact-contract.md for the authoritative artifact lifecycle, status/exit-code rules and output contract. Pure output is a filesystem contract: stdin inputs need no permanent profile file, and default generation leaves only current delivery files. --keep-workspace or explicit --workspace opts into archive retention; never delete user input or existing archives. Runtime scripts are resolved from the Skill installation; candidate artifacts belong to the user's workspace. A Draft is useful output but is never a verified PDF. FAIL and UNVERIFIED are nonzero exits in JSON and human-readable modes.
