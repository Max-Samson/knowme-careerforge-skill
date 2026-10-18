# PDF generation, QA and final rendering

Validation and rendering use scripts/rendering/browser-engine.js. Inspect print media after fonts settle, every page container and visible content boundary; generate a fresh PDF and parse every page for A4 portrait dimensions, allowed page count and extractable content matching the canvas.

PASS requires the actual checks to complete. Missing browser/dependencies or timeout is UNVERIFIED (exit 2), a failed check is FAIL (exit 1). JSON mode uses the same exit rules. Do not use an estimate or an existing PDF as proof. Export verified bytes through a temporary file and atomic replacement; failed export retains the previous file.

The pipeline isolates each run and returns accepted artifact hashes. Default staging is temporary; only explicit --keep-workspace/--workspace retains a manifest. Use this invocation’s PASS output paths, not the existence of a shared default filename. A null manifest in clean mode is expected. Factual and visual review remain Agent responsibilities; text extraction does not certify every ATS. See 07-artifact-contract.md for the complete lifecycle.


## 本地字体与缺字诊断

`forge.py --profile-json` 和 `instantiate-resume.py` 支持 `--font-preset system|arial-unicode`，默认保留系统字体。`arial-unicode` 显式使用本机 Arial Unicode MS；没有该字体时字体验收失败并返回 UNVERIFIED，不保证跨机器可用，也不自动下载字体。字体选择只改变画布样式，不改变 Master 事实，并记录在 Variant 的 source.fontPreset 和运行清单中。

中文 PDF 若文本验收失败，检查 QA 每页的 missingCodepoints、missingFragments 与 extractedRadicals。部首字符可能来自字体字码映射差异，也可能存在真实缺字；不能仅凭这种提示放行。可选用本机可用字体、创建新运行并重新检查，不改写姓名/经历来绕过问题，也不把部首字符全部忽略。

## What each check can actually establish

| Evidence | What it supports | What it cannot establish |
| --- | --- | --- |
| Original user material compared with rewritten claims | Fidelity to supplied facts | Independent verification of the user's history |
| Master/Variant hashes and bound text | Run provenance and rendering consistency | That Agent-written profile claims came from the user |
| Current PDF page/text/layout checks | Technical PDF acceptance | Complete optional information, ideal design or universal ATS support |
| Every page of the final PDF viewed | Actual visual appearance of those pages | Authenticity of the candidate's achievements |

Keep PDF inspection images and helper scripts in system temporary storage, clean your own temporary files afterward, and leave only the delivery pair in the output directory. Inspect the PDF itself using the host's PDF viewer or an available PDF-to-image tool, not a screen-media HTML preview. If no such tool is available, say the PDF's visual review is incomplete; keep the technical PASS distinction. Do not install a second rendering system just to repeat checks the pipeline already performed.

When a font mapping warning occurs, read the failure report’s diagnostics (or archived QA when retention was requested) for missing fragments/codepoints and compare with the source text and page appearance. A warning is a diagnostic clue, not a diagnosis or an automatic reason to force a specific font. Use an available explicit font only as a justified retry; preserve facts and recheck the new PDF. After the current export and review pass, deliver rather than creating more copies or rerunning unchanged checks.

## Production commands (HTML/PDF requests only)

Use the absolute SKILL.md path already returned by the host to resolve `<skill-root>`. The model name does not determine the installation directory: a Gemini model may be running through a host that resolves `.claude/skills`. If unavailable, inspect the host's configured skill location; do not recursively search the home directory. Candidate files belong in the user's workspace, never the installation directory.

After there is sufficient candidate material, and before the first PDF build, run:

```bash
node <skill-root>/scripts/rendering/browser-engine.js --check-runtime
```

READY only checks runtime availability, not resume quality. If unavailable, use its diagnostics and the installed package.json to prepare dependencies once under the host's permission rules. With a lockfile use `npm ci --omit=dev`; otherwise use `npm install --omit=dev`, in `<skill-root>`. Do not guess and install packages one error at a time. If package.json or required bundled scripts are absent, the installation is incomplete: repair it from the project package rather than synthesizing a manifest or installing guessed dependencies. Chromium is also required. If setup is blocked, report UNVERIFIED and offer a requested Draft; do not repeatedly run the full pipeline unchanged.

For a new resume, pass the prepared JSON through stdin. Default clean mode leaves only `resume/resume.html` and `resume/resume.pdf` (or explicit output paths). Do not create profile, analysis, QA, process or history files unless the user requests them:

```bash
python3 <skill-root>/scripts/pipeline/forge.py --profile-json - --role "<target role>" --template <chosen-id>
```

Send the JSON with the command tool's stdin support or `subprocess.run(..., input=json.dumps(profile, ensure_ascii=False), text=True)`; do not interpolate candidate text into a shell command. If the host requires a file, use its temporary-file facility and remove only that newly created input after the command; never delete supplied files.

Choose one layout before building. Do not render all search candidates for comparison unless requested. If an actual visual defect requires a different template, fix the cause and replace the same delivery pair rather than creating named versions. A selected accepted result is already a deliverable: do not rerun merely to obtain another copy.

Drafts use `--draft` and return only `resume/draft.html` by default; they never update the current PDF. Read the exact returned status and paths. A successful preflight need not be repeated on contact or wording updates unless the environment changes. Clean mode reports `manifest: null`: it is intentional, not a missing-file error. Do not search for a run directory or reconstruct deleted diagnostics.

For updates, read the current HTML, apply only the requested changes **in memory**, then submit the full edited HTML to the same pipeline through stdin:

```bash
python3 <skill-root>/scripts/pipeline/forge.py --html-input -
```

Use explicit output paths if the current pair is elsewhere. Do not overwrite the current HTML before validation: the pipeline stages the edit and publishes both files only after acceptance, preserving the old pair on ordinary failures. The report labels this `existing-canvas`, meaning the supplied structure/fonts are preserved, not that a new template was selected. Do not rebuild a profile from rendered text or create backup/version files to make a contact edit.

Use returned diagnostics first; retry only after changing the identified cause. Only when the user requests archives or a specific unresolved failure requires full diagnostic retention, add `--keep-workspace`. An explicit `--workspace <dir>` also retains runs for compatibility with archived workflows. These options deliberately create extra files and are not part of normal resume production. Default temporary intermediates are cleaned on success and failure; existing user files and old archives are never swept or deleted.
