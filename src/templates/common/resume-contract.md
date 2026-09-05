# Resume Universal HTML Contract & A4 Specification (标准通用结构与约束规范)

本文档定义所有简历 HTML 模板必须遵守的**通用 DOM 层次、A4 物理几何约束与数据字段标准**。

---

## 1. A4 物理几何与打印分页约束

所有的简历模板根容器必须严格遵守标准的 A4 页面模型（210mm × 297mm）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>候选人姓名 - 目标岗位 简历</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 每一个 .resume-page 代表一页标准的 A4 页面 -->
  <div class="resume-page" id="page-1">
    <!-- 模板内部组件 -->
  </div>
</body>
</html>
```

### 打印样式必须包含：
```css
@page {
  size: A4 portrait;
  margin: 0; /* 禁用打印机默认边距，完全由 .resume-page 的 padding 接管 */
}

@media print {
  body {
    background: transparent;
    padding: 0;
  }
  .resume-page {
    box-shadow: none;
    margin: 0;
    width: 210mm;
    min-height: 297mm;
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

## 2. 通用数据字段与语义化组件层级

所有模板（单栏、双栏、表格）必须使用以下标准语义化类名：
* **姓名**：`h1.candidate-name`
* **求职目标**：`p.job-target`
* **联系信息**：`ul.contact-list` 或 `div.contact-grid`
* **功能模块**：`section.resume-section`
  * **模块标题**：`h2.section-title`
  * **工作条目**：`div.experience-item`
  * **项目条目**：`div.project-item`
  * **技能容器**：`div.skills-container`
  * **教育条目**：`div.education-item`

## 3. 运行绑定与验收

运行时从 canvas.html 的命名注释槽位装配内容；canvas.html 是每套模板唯一维护的 HTML 结构。sample-profile.json 仅为虚构展示数据，画廊通过同一实例化器与完整 CSS 链生成到 output/templates_gallery，不维护第二份预览结构，也不将样例作为候选人默认值。槽位格式和全集以 scripts/template/instantiate-resume.py 的 SLOTS 为准，缺失、重复或上下文错误的槽位必须失败。共享字段类型与缺失值由 scripts/contracts/profile.py 和 src/knowledge/resume-schema.json 定义。

每个显式 .resume-page 对应一个 A4 页面。--expected-pages 是一页或两页的上限；两页文档需显式分页，不能靠单个超高容器自然流入下一页。验收检查所有容器，并将各页预期正文与最终 PDF 提取文本对应。隐藏、裁剪、缺页和丢字都不能放行。空白草稿不具备 PDF 交付资格。

详见 references/07-artifact-contract.md。PDF 检查通过不是所有第三方 ATS 的认证。
