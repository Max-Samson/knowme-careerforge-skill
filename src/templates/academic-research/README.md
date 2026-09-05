# Academic Research Flow Template (`academic-research`)

> **定位：面向高校硕博、算法科学家、科研人员与学术求职者的高密度单栏学术风模板。**

- **版式风格**：单栏紧凑学术流 (Single-Column Academic Flow)
- **视觉色系**：牛津海军蓝 (`#1e3a8a`, `--palette-deep-navy`) + 板岩灰阶 (`#0f172a`, `#334155`)
- **ATS 评级**：Tier 1 (Optimal - 100% 完美解析)
- **目标页数**：1~2 页 (默认 1 页自包含紧凑布局)
- **信息密度**：极高 (Ultra)
- **核心 Tokens**：
  - `--resume-space-section`: `10pt`
  - `--resume-space-item`: `6.5pt`
  - `--resume-space-bullet`: `2.0pt`
  - `--resume-font-size-body`: `9.0pt`
  - `--resume-line-height-body`: `1.40`
  - `--resume-color-accent`: `var(--palette-deep-navy)`

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
