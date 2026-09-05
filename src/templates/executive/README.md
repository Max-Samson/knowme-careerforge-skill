# Executive Modern Split Template (`executive`)

> **定位：面向技术总监、首席架构师、研发负责人及资深管理者的沉稳大气双栏模板。**

- **版式风格**：顶部深色 Banner + 下方 33:67 双栏 (Hero Banner + Executive Split)
- **视觉色系**：深空板岩灰 (`#1e293b`) + 沉稳松石绿 (`#0f766e`) + 科技天蓝 (`#38bdf8`)
- **ATS 评级**：Tier 1 (Optimal)
- **目标页数**：1~2 页
- **核心 Tokens**：
  - `--resume-left-col-width`: `33%` (默认)
  - `--resume-space-section`: `12pt` (默认)
  - `--resume-space-item`: `9pt` (默认)

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
