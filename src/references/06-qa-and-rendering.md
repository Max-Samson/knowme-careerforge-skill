# QA and final rendering

Validation and rendering use scripts/rendering/browser-engine.js. Inspect print media after fonts settle, every page container and visible content boundary; generate a fresh PDF and parse every page for A4 portrait dimensions, allowed page count and extractable content matching the canvas.

PASS requires the actual checks to complete. Missing browser/dependencies or timeout is UNVERIFIED (exit 2), a failed check is FAIL (exit 1). JSON mode uses the same exit rules. Do not use an estimate or an existing PDF as proof. Export verified bytes through a temporary file and atomic replacement; failed export retains the previous file.

The pipeline isolates each run and records artifact hashes in manifest.json. Use its current PASS output paths, not shared default filenames. Factual and visual review remain Agent responsibilities; text extraction does not certify every ATS. See 07-artifact-contract.md for the complete lifecycle.


## 本地字体与缺字诊断

`forge.py` 和 `instantiate-resume.py` 支持 `--font-preset system|arial-unicode`，默认保留系统字体。`arial-unicode` 显式使用本机 Arial Unicode MS；没有该字体时字体验收失败并返回 UNVERIFIED，不保证跨机器可用，也不自动下载字体。字体选择只改变画布样式，不改变 Master 事实，并记录在 Variant 的 source.fontPreset 和运行清单中。

中文 PDF 若文本验收失败，检查 QA 每页的 missingCodepoints、missingFragments 与 extractedRadicals。部首字符可能来自字体字码映射差异，也可能存在真实缺字；不能仅凭这种提示放行。可选用本机可用字体、创建新运行并重新检查，不改写姓名/经历来绕过问题，也不把部首字符全部忽略。

## What each check can actually establish

| Evidence | What it supports | What it cannot establish |
| --- | --- | --- |
| Original user material compared with rewritten claims | Fidelity to supplied facts | Independent verification of the user's history |
| Master/Variant hashes and bound text | Run provenance and rendering consistency | That Agent-written profile claims came from the user |
| Current PDF page/text/layout checks | Technical PDF acceptance | Complete optional information, ideal design or universal ATS support |
| Every page of the final PDF viewed | Actual visual appearance of those pages | Authenticity of the candidate's achievements |

Inspect the PDF itself using the host's PDF viewer or an available PDF-to-image tool, not a screen-media HTML preview. If no such tool is available, say the PDF's visual review is incomplete; keep the technical PASS distinction. Do not install a second rendering system just to repeat checks the pipeline already performed.

When a font mapping warning occurs, read the reported missing fragments/codepoints and compare with the source text and page appearance. A warning is a diagnostic clue, not a diagnosis or an automatic reason to force a specific font. Use an available explicit font only as a justified retry; preserve facts and recheck the new PDF. After the current export and review pass, deliver rather than creating more copies or rerunning unchanged checks.
