# Table Structured Classic Template (`classic`)

> **定位：面向国企、金融机构、政企合规岗位及传统名企的高密度结构化表格模板。**

- **版式风格**：6 列现代矩阵网格 (Structured Table Grid)
- **视觉色系**：商务蓝 (`#1d4ed8`) + 板岩灰边框 (`#cbd5e1`) + 柔和浅灰标签背景 (`#f1f5f9`)
- **ATS 评级**：Tier 1 (Optimal - 规范表格语义)
- **目标页数**：严格 1 页
- **核心 Tokens**：
  - `--resume-cell-padding`: `4.5pt 7pt` (默认)
  - `--resume-font-size-body`: `9pt` (默认)
  - `--resume-color-accent`: `#1d4ed8` (默认)

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
