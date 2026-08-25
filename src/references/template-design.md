# Reference Manual: Template Design & Tokens (模板设计与 Token 体系)

---

## 1. 物理 A4 印刷尺寸与 CSS Paged Media

```css
@page {
  size: A4 portrait;
  margin: 0; /* 消除默认打印边距，由容器内边距接管 */
}

@media print {
  body { background: transparent; padding: 0; }
  .resume-page {
    width: 210mm;
    height: 297mm;
    page-break-after: always;
    page-break-inside: avoid;
  }
  .avoid-break {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}
```

---

## 2. 核心 Design Tokens 字典

```css
:root {
  /* 色彩系统 (Slate / Blue 阶梯) */
  --resume-color-primary: #0f172a;       /* 正文主要文字 (Slate 900) */
  --resume-color-secondary: #334155;     /* 次要文字与日期 (Slate 700) */
  --resume-color-muted: #64748b;         /* 辅助文字 (Slate 500) */
  --resume-color-accent: #2563eb;        /* 主题强调色 (Blue 600) */
  --resume-color-border: #e2e8f0;        /* 分隔线与边框 (Slate 200) */
  --resume-color-tag-bg: #f1f5f9;        /* 技能标签背景 (Slate 100) */

  /* 字阶系统 */
  --resume-font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --resume-font-size-name: 20pt;
  --resume-font-size-target: 10.5pt;
  --resume-font-size-h2: 12pt;
  --resume-font-size-body: 9.2pt;
  --resume-font-size-meta: 8.5pt;
  --resume-line-height-body: 1.45;

  /* 间距 Tokens (Agent 调参自愈核心变量) */
  --resume-space-header-bottom: 11pt;
  --resume-space-section: 11pt;
  --resume-space-item: 7.5pt;
  --resume-space-bullet: 2.5pt;
}
```
