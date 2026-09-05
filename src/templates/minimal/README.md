# Minimal Tech Template (`minimal`)

> **定位：面向技术研发、AI 算法与系统工程师的高密度单栏极简模板。**

- **版式风格**：单栏线性流 (Single-Column Linear Flow)
- **视觉色系**：极客蓝 (`#2563eb`) + 板岩灰阶 (`#0f172a`, `#334155`)
- **ATS 评级**：Tier 1 (Optimal - 100% 完美解析)
- **目标页数**：严格 1 页 (支持微调扩展至 2 页)
- **核心 Tokens**：
  - `--resume-space-section`: `11pt` (默认)
  - `--resume-font-size-body`: `9.2pt` (默认)
  - `--resume-space-item`: `7.5pt` (默认)

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
