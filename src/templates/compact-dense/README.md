# Compact Dense Grid Template (`compact-dense`)

> **定位：面向 8~15 年资深系统架构师、全栈技术专家的高信息密度极致单页模板。**

- **版式风格**：极致紧凑网格流 (Compact Dense Grid Flow)
- **视觉色系**：钢铁蓝 (`#0369a1`) + 暗板岩色 (`#1e293b`, `#0f172a`)
- **ATS 评级**：Tier 1 (Optimal - 100% 完美解析)
- **目标页数**：严格 1 页 (在单页 A4 物理空间内容纳超高信息量)
- **信息密度**：极高 (Ultra)
- **核心 Tokens**：
  - `--resume-space-section`: `8.5pt`
  - `--resume-space-item`: `5.5pt`
  - `--resume-space-bullet`: `1.5pt`
  - `--resume-font-size-body`: `8.8pt`
  - `--resume-line-height-body`: `1.38`
  - `--resume-color-accent`: `#0369a1`

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
