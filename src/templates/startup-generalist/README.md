# Startup Generalist Cards Template (`startup-generalist`)

> **定位：面向早期初创公司 0~1 核心骨干、独立开发者与增长工程师的模块化卡片流模板。**

- **版式风格**：模块化卡片流 (Modular Cards Flow)
- **视觉色系**：活力翡翠绿 (`#059669`, `--palette-emerald-fresh`) + 板岩灰阶 (`#1e293b`, `#334155`)
- **ATS 评级**：Tier 1 (Optimal - 100% 完美解析)
- **目标页数**：1 页
- **信息密度**：高 (High)
- **核心 Tokens**：
  - `--resume-space-section`: `10pt`
  - `--resume-space-item`: `7pt`
  - `--resume-space-bullet`: `2.0pt`
  - `--resume-font-size-body`: `9.0pt`
  - `--resume-line-height-body`: `1.42`
  - `--resume-color-accent`: `var(--palette-emerald-fresh)`

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
