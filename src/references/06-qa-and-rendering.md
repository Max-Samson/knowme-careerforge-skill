# Reference Manual 06: Automated Dual QA & Deterministic PDF Export

> **"Validate before delivery. Output pixel-perfect PDF only after 100% Dual QA compliance."**

---

## 1. Automated Dual QA Protocol

Before rendering the final PDF, run the validation toolchain against `workspace/resume.html`:

```bash
# 1. Layout & Physical A4 Height QA
python3 scripts/validation/validate-resume.py --html workspace/resume.html --expected-pages 1

# Or with Playwright DOM inspection (when node/ts available):
npx ts-node scripts/validation/validate-layout.ts --html workspace/resume.html --expected-pages 1
```

### Physical Dimension Benchmarks:
- Standard A4 Height at 96 DPI: $297\text{mm} \times 96 / 25.4 = 1122.5\text{px}$
- Allowed Threshold for 1-Page Resume: $\le 1123\text{px}$
- If reported height > 1123px (e.g. 1145px, +22px overflow):
  1. Trigger Self-Healing: reduce `--resume-space-section` by 1.5pt and `--resume-font-size-body` by 0.2pt;
  2. Condense verbose descriptions while keeping evidence intact;
  3. Re-run `validate-resume.py` until 100% PASS.

---

## 2. ATS Compatibility Verification

```bash
npx ts-node scripts/validation/validate-ats.ts --html workspace/resume.html
```

### ATS Check Rules:
- [ ] Text extractability: 100% of resume content must be plain HTML text (no text embedded inside raster images);
- [ ] Contact completeness: Phone, email, location, and name must be discoverable via standard regex;
- [ ] Heading hierarchy: Exactly one `h1.candidate-name`, standard `h2.section-title` for major sections;
- [ ] Table/Grid compliance: All tabular data must have clean linear textual fallback for screen readers.

---

## 3. Deterministic PDF Rendering

```bash
# Auto-discovery multi-strategy PDF export (Playwright -> Chrome -> Edge -> Brave)
python3 scripts/rendering/render-pdf.py workspace/resume.html workspace/resume.pdf --quiet
```

### Rendering Invariants:
- Uses `@page { size: A4 portrait; margin: 0; }`
- Forces `printBackground: true` and `preferCSSPageSize: true`
- Waits for `document.fonts.ready` before snapshotting
- Output artifact: `workspace/resume.pdf` (Lossless vector PDF)
