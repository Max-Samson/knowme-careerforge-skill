# Modern Split Sidebar Template (`modern`)

> **定位：面向现代全栈工程师、AI 工程师及海外远程求职者的经典双栏模板。**

- **版式风格**：左右双栏黄金比例 (32:68 Sidebar Split)
- **视觉色系**：深海蓝 (`#254665`) + 天空蓝高亮 (`#38bdf8`)
- **ATS 评级**：Tier 1 (Optimal - 线性流 DOM 结构)
- **目标页数**：1~2 页
- **核心 Tokens**：
  - `--resume-sidebar-width`: `32%` (默认)
  - `--resume-space-section`: `12pt` (默认)
  - `--resume-font-size-body`: `9.2pt` (默认)

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
