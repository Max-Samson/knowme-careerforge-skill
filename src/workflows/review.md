# Workflow 6: Review & QA (双重质检与自愈闭环)

> **目标：自动化验证 ATS 纯文本可解析性与 DOM 高度溢出，闭环自愈调参，导出确定性 PDF。**

---

## 1. 双重 QA 自动化测试

1. **测试 1：布局与 DOM 高度溢出检测**：
   ```bash
   python3 scripts/validate-resume.py --html workspace/resume.html --expected-pages 1
   ```
   - 单页标准高度：$297\text{mm} \times 96\text{DPI} / 25.4 \approx 1122.5\text{px}$。
2. **测试 2：ATS 纯文本流解析检测**：
   ```bash
   npx ts-node scripts/validate-ats.ts --html workspace/resume.html
   ```

## 2. 自动化自愈修复闭环

- **若发生页面溢出（如高度 1145px > 1122.5px）**：
  1. 在 `workspace/resume.html` 的 `<style>` 中微调 `--resume-space-section: 9.5pt;`；
  2. 微调 `--resume-font-size-body: 9.0pt;`；
  3. 精简多余空行或过长描述；
  4. 重新运行验证脚本直至 100% 通过。

## 3. 确定性无损 PDF 导出

```bash
npx ts-node scripts/render-pdf.ts --input workspace/resume.html --output workspace/resume.pdf
```
