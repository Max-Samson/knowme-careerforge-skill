# Browser rendering and validation

All rendering/layout entry points delegate to `browser-engine.js`:

```js
const { run } = require('./browser-engine');
const result = await run(htmlPath, { expectedPages: 1, autoHeal: false, outputPdf });
```

```sh
node scripts/rendering/browser-engine.js resume.html --expected-pages 1 --output resume.pdf
```

CLI stdout is one JSON object with `status`, `errors`, `warnings`, `checks`,
`file`, and `expectedPages`. Exit codes: PASS=0, FAIL=1, UNVERIFIED=2.
`expectedPages` is an upper limit, restricted to 1 or 2.
Missing dependencies, browser/font/resource failures and parser failures cannot pass.
Validation without `outputPdf` still generates and inspects a fresh in-memory PDF.
No previous PDF is read to decide success. Output write/publication failures are
FAIL (exit 1); UNVERIFIED is reserved for unavailable verification facilities.
On successful export, `checks.output` contains `status: "PASS"`, `committed: true`,
the absolute `path`, and lowercase SHA-256 `pdfSha256` / `htmlSha256` digests of
the exact published PDF and final source HTML bytes. Without export, `committed`
is false and `path` is null, while digests identify the verified in-memory PDF
and final HTML.

Runtime dependencies: Playwright (or playwright-core with a browser), pdf-lib,
and pdfjs-dist with `legacy/build/pdf.mjs`; use a Node version supported by
pdfjs-dist. `CHROME_BIN` / `BROWSER_PATH` can select a Chromium executable.
Without overrides, bundled Chromium is tried first, then detected system
Chrome/Chromium/Edge/Brave installations (including PATH and macOS/Windows locations).
Dependency installation and package manifests are managed separately.

Checks use print media, await fonts and images, and inspect every `.resume-page`,
its descendants and text ranges against all four boundaries and rectangular
ancestor clips. Exactly one nonempty visible `h1.candidate-name` is required,
Nonempty print-hidden body text (display, visibility or ancestor opacity) fails,
even if other body text still survives PDF extraction. Also required:
at least 20 non-whitespace body characters beyond the name with no unbound
resume slot comments or language attribute. Literal brace syntax in user text is preserved. Each PDF page must correspond to an explicit `.resume-page`;
a single root naturally flowing into multiple PDF pages is rejected. DOM tolerance is 0.75 CSS pixels. Unsupported clipping returns
UNVERIFIED. The generated PDF must have 1–`expectedPages` portrait A4
pages (1 PDF point tolerance, including crop boxes). PDF.js extracts every page:
normalized character multiplicities and each DOM text fragment must survive on
the corresponding PDF page. NFKC and whitespace/control normalization tolerate
line wrapping and ligatures; a missing or reordered name cannot pass.

Autoheal only reduces existing numeric inline `:root` tokens through the bounded
ladder. Each candidate is loaded from a temporary sibling HTML file to preserve
relative assets and fully revalidated. No source change is published on failed
validation. On success, files are replaced by same-directory renames; an HTML
backup allows rollback if PDF publication fails. This is per-file atomicity with
rollback, not a crash-atomic transaction spanning two files. Temporary candidates
are cleaned up. Concurrent source edits detected before publication abort the run.

Isolated tests (real Chromium, temporary directories and injected PDF/I/O failures):

```sh
node --test tests/rendering/browser-engine.test.js
python3 scripts/build/run-all-tests.py
```

The Python suite runs the Node regressions through `tests/validation/test_auto_heal.py`.

Per-page text diagnostics include missingCodepoints and extractedRadicals (glyph and U+ codepoint). A warning about possible font mapping differences never changes FAIL to PASS. The pipeline and instantiator accept --font-preset arial-unicode to explicitly use locally installed Arial Unicode MS; this is not a browser-engine option. Missing explicit fonts remain UNVERIFIED.
