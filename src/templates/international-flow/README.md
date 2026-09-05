# International Text Flow Template (`international-flow`)

> **定位：面向外企跨国求职、海外远程 (US/EU) 及全球化技术专家的欧美极简纯文字流模板。**

- **版式风格**：单栏纯文字流 (Single-Column Pure Text Flow)
- **合规特性**：严格遵守海外劳动反歧视法标准，无头像/照片干扰，注重文本可提取性
- **视觉色系**：极简板岩黑 (`#0f172a`, `--palette-slate-minimal`) + 碳素灰阶 (`#334155`)
- **ATS 评级**：Tier 1 (Optimal - 100% 完美解析)
- **目标页数**：1~2 页 (默认 1 页均衡排版)
- **信息密度**：中等 (Balanced)
- **核心 Tokens**：
  - `--resume-space-section`: `11pt`
  - `--resume-space-item`: `7.5pt`
  - `--resume-space-bullet`: `2.2pt`
  - `--resume-font-size-body`: `9.2pt`
  - `--resume-line-height-body`: `1.45`
  - `--resume-color-accent`: `var(--palette-slate-minimal)`

## 文件维护

- `canvas.html`：唯一维护的 HTML 布局，包含统一命名槽位。
- `style.css`：此模板的样式与设计变量。
- `sample-profile.json`：仅供画廊使用的虚构样例数据，不作为用户简历默认值。
- `metadata.json`：模板选择与布局元数据。

在项目根目录运行 `python3 scripts/build/build-gallery.py` 生成画廊。预览与实际简历共用实例化器及完整 CSS 链；生成的 HTML 位于 `output/templates_gallery/`，不回写到模板源目录。
