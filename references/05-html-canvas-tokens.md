# HTML canvas and tokens

Instantiate an empty canvas.html skeleton with explicit user facts. canvas.html is the sole maintained structure. Gallery previews bind explicit fictional sample-profile.json through the same instantiator and full CSS chain; sample data must never serve as default candidate facts. Shared normalization accepts omitted/null optional fields and rejects invalid types. Failed binding must preserve old output and return nonzero.

Tune the run's HTML with CSS variables for section/item/bullet spacing and body typography. Preserve manually edited content rather than regenerating stale profile data. Auto-healing cannot remove facts or reduce body font below 8.8pt. Validate in print mode, inspect all pages and verify the actual PDF before delivery. See 07-artifact-contract.md.


## 本地字体与缺字诊断

`forge.py` 和 `instantiate-resume.py` 支持 `--font-preset system|arial-unicode`，默认保留系统字体。`arial-unicode` 显式使用本机 Arial Unicode MS；没有该字体时字体验收失败并返回 UNVERIFIED，不保证跨机器可用，也不自动下载字体。字体选择只改变画布样式，不改变 Master 事实，并记录在 Variant 的 source.fontPreset 和运行清单中。

中文 PDF 若文本验收失败，检查 QA 每页的 missingCodepoints、missingFragments 与 extractedRadicals。部首字符可能来自字体字码映射差异，也可能存在真实缺字；不能仅凭这种提示放行。可选用本机可用字体、创建新运行并重新检查，不改写姓名/经历来绕过问题，也不把部首字符全部忽略。
