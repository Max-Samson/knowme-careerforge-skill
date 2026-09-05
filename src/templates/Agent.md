# KnowMe CareerForge — Templates Architecture & AI Agent Design System Specification

> **定位**：面向 AI Agent 与前端/模板研发工程师的 `src/templates/` 模板矩阵架构规范、两层 Design Tokens 体系、DOM 语义化契约与扩展开发指南。  
> **版本**：v1.0.0-matrix  
> **核心原则**：Single-File Self-Contained · Two-Tier Tokens · Deterministic A4 Geometry · Heuristic Auto-Healing · Zero External Assets

---

## 1. 模板矩阵全景与分类架构 (The 10-Template Matrix)

KnowMe CareerForge 采用**场景细分、按岗定制**的模板工程矩阵。全量 10 套模板均严格遵守 A4 物理几何与单文件自包含规范：

| 模板 ID | 版式构图比例 | 视觉色调与调色板 | 目标人群与适用场景 | 目标页数 | 信息密度 | ATS 评级 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`minimal`** | 单栏极简线性流 | Geek Blue (`#2563eb`) + Slate | 技术研发、通用工程师、DevOps、系统级开发 | 1 页 | 高 (High) | Tier 1 |
| **`modern`** | 左右分栏 (32:68) | Modern Deep Navy (`#254665`) + Slate | 前端、后端、全栈架构、AI Agent 工程师 | 1 页 | 均衡 (Balanced) | Tier 1 |
| **`executive`** | Hero Banner + 双栏 (33:67) | Executive Teal (`#0f766e`) + Dark Slate | 首席架构师、技术总监、CTO、资深产品专家 | 1~2 页 | 均衡 (Balanced) | Tier 1 |
| **`classic`** | 结构化网格表格流 | Corporate Blue (`#1d4ed8`) + Slate | 国企、央企、外企传统部门、金融科技、政务 | 1 页 | 高 (High) | Tier 1 |
| **`academic-research`** | 单栏紧凑学术风 | Oxford Navy (`#1e3a8a`) + Slate | 高校硕博、算法科学家、研究员；强化论文与引用 | 1~2 页 | 极高 (Ultra) | Tier 1 |
| **`international-flow`** | 欧美极简纯文字流 (无头像) | Neutral Slate (`#0f172a`) + Charcoal | 外企跨国求职、海外远程 (US/EU)；严格遵守反歧视法 | 1~2 页 | 均衡 (Balanced) | Tier 1 |
| **`creative-tech`** | 非对称双栏 (28:72) + 胶囊标签 | Tech Violet (`#7c3aed`) + Indigo | 前端专家、UI/UX 研发、创意技术岗；突出交互与体验 | 1 页 | 均衡 (Balanced) | Tier 1 |
| **`compact-dense`** | 极致紧凑双列网格 | Steel Blue (`#0369a1`) + Dark Slate | 8~15 年资深工程师、架构师；单页容纳超高信息量 | 1 页 | 极高 (Ultra) | Tier 1 |
| **`startup-generalist`** | 模块化卡片流 | Emerald Green (`#059669`) + Slate | 初创团队 0~1 骨干、独立开发者；突出商业与增长成果 | 1 页 | 高 (High) | Tier 1 |
| **`data-analyst`** | 指标驱动双栏 (30:70) | Amber Cyan (`#0891b2`) + Slate | 数据科学家、BI 专家、增长架构师；强化量化看板 | 1 页 | 高 (High) | Tier 1 |

---

## 2. 两层 Design Tokens 体系与调色板规范 (Two-Tier Tokens)

模板体系严格遵循 ADR-0002 与 ADR-0003 的两层 Tokens 架构：

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Primitive Tokens (底层常量池，定义于 common/base.css)     │
│    - 物理尺寸: 210mm × 297mm (1122.5px @ 96 DPI)            │
│    - 色彩阶梯: Slate 50~900, 官方主题调色板预设               │
│    - 间距阶梯: 2pt / 4px 基准网格 (space-1 ~ space-12)       │
│    - 字号阶梯: display(22pt) -> title(18pt) -> body(9.2pt) │
└──────────────────────────────┬──────────────────────────────┘
                               │ 继承与语义映射
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Component Tokens (组件/模板层变量，定义于各模板 style.css) │
│    - --resume-color-primary: 文本主色                        │
│    - --resume-color-accent:  主视觉强调色                     │
│    - --resume-space-section: 模块间距 (核心自愈参数)           │
│    - --resume-space-item:    条目间距 (核心自愈参数)           │
│    - --resume-space-bullet:  列表行间距 (核心自愈参数)         │
│    - --resume-font-size-body: 正文字号 (>= 8.8pt 物理底线)    │
│    - --resume-line-height-body: 正文行高 (1.38 ~ 1.45)        │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 官方 6 大主题调色板预设 (Official Palette Presets)
在 `src/templates/common/base.css` 中固化定义，可通过 Component Token 一键映射：
- `--palette-tech-blue`: `#2563eb` (经典科技蓝 — 通用工程、前端/全栈、技术架构)
- `--palette-deep-navy`: `#1e3a8a` (深邃海航蓝 — 学术科研、算法科学家、深度模型研究)
- `--palette-teal-modern`: `#0f766e` (现代松石绿 — 首席架构师、CTO、产品总监)
- `--palette-emerald-fresh`: `#059669` (活力翡翠绿 — 早期初创公司、增长黑客、独立开发)
- `--palette-violet-creative`: `#7c3aed` (创意极光紫 — 前端 UI/UX、交互动效、设计系统)
- `--palette-slate-minimal`: `#334155` (极简碳素灰 — 跨国求职、海外远程、纯文本合规)

---

## 3. 通用 DOM 语义化结构契约 (Universal DOM Contract)

所有模板必须严格遵循标准 DOM 层次，保证 `scripts/template/instantiate-resume.py` 能够进行无损数据注入，且 100% 通过 ATS 解析引擎：

### 3.1 根容器与 A4 打印契约
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>候选人姓名 - 目标岗位简历</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 每一个 .resume-page 代表一页标准物理 A4 容器 -->
  <div class="resume-page" id="page-1">
    <!-- 模板内部组件 -->
  </div>
</body>
</html>
```

### 3.2 必须遵循的标准语义类名与 ID
| 模块/元素 | 约定选择器 | 规范说明 |
| :--- | :--- | :--- |
| **候选人姓名** | `h1.candidate-name` | ATS 首要提取字段，字号通常为 18~22pt |
| **求职意向** | `p.job-target` 或 `.candidate-title` | 明确标注目标职能，增强岗位匹配度 |
| **价值主张** | `p.value-prop` | 15~25 字高度浓缩的核心竞争优势陈述 |
| **联系方式网格** | `div.contact-grid` 或 `ul.sidebar-info-list` | 包含电话、邮箱、城市、GitHub 等关键事实 |
| **专业技能模块** | `<section class="resume-section" id="skills">` | 标头必须为 `h2.section-title`（"专业技能" / "Technical Skills"） |
| **技能条目行** | `div.skills-content > .skill-row` | 分类名 `.skill-category` + 具体项 `.skill-items` |
| **工作经历模块** | `<section class="resume-section" id="experience">` | 标头为 `h2.section-title`（"工作经历" / "Work Experience"） |
| **工作经历条目** | `div.experience-item` | 包含公司名 `.org-name`、职位标签 `.role-badge`、时间 `.date-range` |
| **核心项目模块** | `<section class="resume-section" id="projects">` | 标头为 `h2.section-title`（"核心项目" / "Key Projects"） |
| **项目经历条目** | `div.project-item` | 包含项目名 `.project-name`、技术栈胶囊 `.tech-stack-tags > .tech-tag` |
| **教育背景模块** | `<section class="resume-section" id="education">` | 标头为 `h2.section-title`（"教育背景" / "Education"） |
| **成就/工作要点** | `ul.bullet-list > li` | 动词开头 + FAB 成果量化陈述 |

---

## 4. 启发式自愈与排版调谐算法契约 (Auto-Healing Ladder)

当生成的 HTML 画布物理渲染高度超出 A4 允许极限（单页 $> 1122.5\text{px}$）时，系统调度 `scripts/validation/validate-resume.py --auto-heal` 执行阶梯式参数收敛，无需 Agent 手动猜值：

```text
┌─────────────────────────────────────────────────────────────┐
│ 启发式 Design Tokens 自愈执行阶梯                           │
├─────────────────────────────────────────────────────────────┤
│ 阶段 1 (模块间距 Section Spacing):                           │
│   --resume-space-section: 10.5pt ➔ 9.5pt ➔ 8.5pt            │
│                                                             │
│ 阶段 2 (条目与列表项间距 Item & Bullet Spacing):             │
│   --resume-space-item:    7.0pt  ➔ 6.0pt  ➔ 5.0pt           │
│   --resume-space-bullet:  2.5pt  ➔ 2.0pt  ➔ 1.5pt           │
│                                                             │
│ 阶段 3 (字号与行高微调 Typography Scale):                     │
│   --resume-font-size-body:   9.0pt ➔ 8.8pt (物理安全底线!)   │
│   --resume-line-height-body: 1.42  ➔ 1.38                   │
│                                                             │
│ 阶段 4 (若仍溢出，输出内容精简建议 Content Condensation):     │
│   计算溢出 ΔH ➔ 输出超标行数、超标字数与目标 DOM 节点选择器    │
└─────────────────────────────────────────────────────────────┘
```

### 4.1 物理安全底线约束 (Inviolable Bounds)
1. **字号底线**：`--resume-font-size-body` 绝对不允许低于 `8.8pt`（约 `11.7px`），防止打印成纸质版时因字号过小失去可读性；
2. **步长规范**：间距调整必须严格按照 $0.5\text{pt}$ 或 $1\text{pt}$ 的离散倍数递减，严禁随机填入非标浮点数值；
3. **单文件内联写入**：自愈器直接对 `workspace/resume.html` 的 `:root` 代码块执行就地更新，完全保持单文件独立性。

---

## 5. AI Agent 开发与新增模板扩展规范 (Developer Guidelines)

当研发人员或 AI Agent 需要在 `src/templates/` 下增加新模板时，必须遵循以下工程纪律：

### 5.1 新增模板必须包含的“四件套”
每个模板目录名必须为全小写连字符（如 `new-style`），且必须包含以下 4 个标准文件：
1. **`template.html`**：
   - 语义化 HTML5 骨架，根容器为 `<div class="resume-page" id="page-1">`；
   - 必须引入 `<link rel="stylesheet" href="style.css">`（在实例化阶段会被脚本内联替换为 `<style>`）；
   - 包含符合第 3 节契约的默认占位内容。
2. **`style.css`**：
   - 顶部声明 `:root { ... }`，提供本模板完整的 Component Tokens；
   - 必须定义第 3 节中约定的全部通用类名（包括 `.experience-item`、`.project-item`、`.tech-tag`、`.bullet-list` 等）；
   - 包含 `@media print` 打印媒体查询与分页规整规则。
3. **`metadata.json`**：
   - 声明模板多维检索属性，供 `search-template.py` 算法进行推荐匹配。必须包含以下字段：
   ```json
   {
     "id": "new-style",
     "name": "Human Readable Name",
     "version": "1.0.0",
     "style": "single-column-flow",
     "roleCategory": "engineering-ai",
     "layout": {
       "type": "single-column",
       "targetPages": 1,
       "maxPages": 1,
       "density": "high"
     },
     "visualStyle": {
       "tone": "tech-blue",
       "accentColor": "#2563eb",
       "fontFamily": "System Sans-Serif"
     },
     "atsScoreTier": "tier-1-optimal",
     "supportedRoles": ["frontend", "backend", "fullstack"],
     "languages": ["zh-CN", "en-US"],
     "customizableTokens": [
       "--resume-font-size-body",
       "--resume-line-height-body",
       "--resume-space-section",
       "--resume-space-item",
       "--resume-space-bullet",
       "--resume-color-accent"
     ]
   }
   ```
4. **`README.md`**：
   - 简短明了说明该模板的设计理念、视觉基调、适用岗位以及默认 Tokens 参数。

### 5.2 模板编译与注册验证工作流
新增模板后，必须依次运行以下命令完成系统注册与画廊同步：

```bash
# 1. 扫描 src/templates/，重新编译全量知识库索引 (生成 src/knowledge/templates.json)
python3 scripts/build/build-knowledge.py

# 2. 重新编译本地静态交互式画廊预览
python3 scripts/build/build-gallery.py

# 3. 运行全量自动化测试套件 (包含 30+ 项模板契约、ATS 与自愈测试)
python3 scripts/build/run-all-tests.py
```

### 5.3 严格禁止的八大反模式 (Anti-Patterns to Avoid)
- ❌ **严禁外链网络资产**：严禁在模板中引入 Google Fonts、外部 CDN 图标库或在线 CSS。所有样式与图标必须自包含；
- ❌ **严禁隐藏文本欺骗 ATS**：严禁使用 `opacity: 0`、`font-size: 0` 或 `display: none` 堆砌作弊关键词；
- ❌ **严禁把文字做成图片**：标题、联系方式、经历必须为纯文本 DOM，保证 ATS 提取率 100%；
- ❌ **严禁污染外部上下文**：模板 CSS 必须限定在 `.resume-page` 命名空间内部，禁止对全局 `html` 增加不可预期的覆盖；
- ❌ **严禁硬编码像素死值**：模块间距、条目间距必须使用 `var(--resume-space-*)`，确保 `--auto-heal` 算法可以接管调优；
- ❌ **严禁丢失核心类名**：即使是创意模板，也必须提供标准类名别名（如 `.experience-item`），否则数据注入引擎将无法命中替换；
- ❌ **严禁在 Git 中提交 build 预览物**：编译出的 `output/templates_gallery/` 纯属本地展示构建物，绝不提交至版本库；
- ❌ **严禁违背物理 A4 标准**：宽度必须严格保证 `210mm`，且打印样式中 `@page { margin: 0; }`。
