# QA and final rendering

Validation and rendering use scripts/rendering/browser-engine.js. Inspect print media after fonts settle, every page container and visible content boundary; generate a fresh PDF and parse every page for A4 portrait dimensions, allowed page count and extractable content matching the canvas.

PASS requires the actual checks to complete. Missing browser/dependencies or timeout is UNVERIFIED (exit 2), a failed check is FAIL (exit 1). JSON mode uses the same exit rules. Do not use an estimate or an existing PDF as proof. Export verified bytes through a temporary file and atomic replacement; failed export retains the previous file.

The pipeline isolates each run and records artifact hashes in manifest.json. Use its current PASS output paths, not shared default filenames. Factual and visual review remain Agent responsibilities; text extraction does not certify every ATS. See 07-artifact-contract.md for the complete lifecycle.


## 本地字体与缺字诊断

`forge.py` 和 `instantiate-resume.py` 支持 `--font-preset system|arial-unicode`，默认保留系统字体。`arial-unicode` 显式使用本机 Arial Unicode MS；没有该字体时字体验收失败并返回 UNVERIFIED，不保证跨机器可用，也不自动下载字体。字体选择只改变画布样式，不改变 Master 事实，并记录在 Variant 的 source.fontPreset 和运行清单中。

中文 PDF 若文本验收失败，检查 QA 每页的 missingCodepoints、missingFragments 与 extractedRadicals。部首字符可能来自字体字码映射差异，也可能存在真实缺字；不能仅凭这种提示放行。可选用本机可用字体、创建新运行并重新检查，不改写姓名/经历来绕过问题，也不把部首字符全部忽略。
