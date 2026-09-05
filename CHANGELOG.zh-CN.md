# 更新日志 (Changelog)

**KnowMe CareerForge** 项目的所有重要版本演进与功能变更均记录于此文档。

本日志格式严格遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范，版本号遵守 [语义化版本 (Semantic Versioning)](https://semver.org/lang/zh-CN/) 标准。

---
## [0.0.7] - 2026-09-06

本修复版本结合 Claude 与 Gemini 的真实使用过程，统一跨 Agent 简历制作流程，收紧事实改写边界，并简化安装准备与最终交付。

### 新增 (Added)

- 新增 `browser-engine.js --check-runtime`，集中报告缺失的运行依赖并检查浏览器启动，不生成候选人产物；`READY` 仅表示环境可用，不表示简历验收通过。同时补充命令行帮助。
- 新增 `forge.py --summary`，简短返回当前 HTML/PDF 交付路径与 manifest 位置，完整诊断继续保存在运行目录。
- 新增 `search-template.py --summary`，仅返回前三个候选布局，避免重复输出完整元数据；原有完整 JSON 与排序保持不变。
- 补充隔离安装、平台入口路径、重复安装、运行诊断、简短报告及教育排版回归覆盖。

### 优化 (Changed)

- 各平台适配统一引用 `SKILL.md` 工作流。先判断候选人资料是否可用，再读取资源；资料不足时，内容编写与渲染共同等待，可选字段缺失不再强制进入 Draft。
- 改写规范要求对照用户原始材料，检查技术、职责、范围、实现机制、成果与确定程度。岗位知识和示例不作为候选人事实，用户接受草稿也不为 Agent 自行添加的内容提供事实依据。
- 默认只交付一个当前版本的 PDF 与可编辑 HTML，说明实际模板和必要缺项；内部快照与 QA 不再混入默认交付。局部更新保留无关文案、模板选择与交付文件名。
- 模板指南覆盖全部十套布局，依据真实内容与可读性选择；移除强制 FAB 成果表达及未经验证的 ATS 关键词密度要求，明确事实复核、技术 PDF 验收与视觉检查的不同含义。

### 修复 (Fixed)

- 修复安装包缺少运行依赖声明的问题，安装时携带 `package.json`，存在 `package-lock.json` 时一并复制，并明确依赖准备命令。
- 修复 Cursor/Windsurf 配置缺少配套运行资源与明确入口路径的问题；Gemini 配置指向实际安装的运行入口。
- 修复安装失败后仍统一提示成功，以及重复安装 Windsurf 时不断追加托管规则的问题。
- 修复教育条目缺少学校或日期时，学历与专业被分散到两端的问题；实际日期继续保持右对齐。

### 升级说明 (Upgrade notes)

- 使用更新后的包重新执行 `knowme init --ai <platform>`，刷新已安装指令与资源。在安装目录准备依赖：有锁文件时执行 `npm ci --omit=dev`，否则执行 `npm install --omit=dev`，随后运行环境预检。
- 默认及 `--quiet` 报告格式保持兼容，`--summary` 为可选简短输出；保留历史运行记录及验收副本的失败保护。
- 自动检查验证工具行为与 PDF 输出，不证明候选人经历真实，也不保证所有宿主均遵循指令；升级后仍需验证真实宿主的使用效果。

---

## [0.0.6] - 2026-09-05

本版本扩展简历模板库，完善从用户事实保留、模板装配到最终 PDF 验收的生成流程，提升简历制作与交付的可靠性。

### 新增 (Added)

- 新增 `academic-research`、`international-flow`、`creative-tech`、`compact-dense`、`startup-generalist`、`data-analyst` 六套模板，模板总数增至十套，并提供六组主题调色板预设。
- 新增 Draft、Master、Variant 资料管理，分别支持不完整草稿、可复用事实档案与岗位定制简历，并记录来源版本。
- 为每次生成创建独立工作区，保存输入快照、可编辑 HTML、校验报告和交付清单。
- 新增 `--auto-heal`，在限定范围内自动调整间距和字号；调整失败保留原画布，不改写候选人事实强行适配页数。
- 新增 `--font-preset system|arial-unicode` 及字体诊断，支持排查 PDF 文本提取问题。

### 优化 (Changed)

- 明确以用户描述、已有简历和提供的辅助材料制作简历，由宿主 Agent 理解内容并进行岗位定制，工具链负责校验、排版和导出。
- 每套模板统一由 `canvas.html` 维护结构，展示样例单独存储；画廊预览与实际简历共用生成流程和样式。
- Python、TypeScript 打印与 PDF 导出入口共用校验引擎，在交付前检查字体、所有页面布局、A4 尺寸及最终 PDF 文本。
- 生成结果统一为 `DRAFT`、`PASS`、`FAIL`、`UNVERIFIED`，本次运行的 manifest 记录交付路径及已验收产物摘要。
- 完善 Skill 元数据、使用指南和架构文档，新增 `AGENTS.md` 开发入口及对齐 Agent Skills 的包设计规范。
- 扩充资料绑定、产物隔离、画廊一致性及浏览器/PDF 验收回归覆盖。

### 修复 (Fixed)

- 修复不完整资料混入展示样例，以及缺失字段被补成无依据候选人事实的问题。
- 修复多条教育记录相互覆盖，以及绑定时遗漏工作、项目和教育详情的问题。
- 修复非法模板槽位、未转义文本和关键词高亮导致的 HTML 异常；绑定失败时保留原有输出。
- 修复渲染或校验失败后，仍将旧 PDF 误报为本次成功交付的问题。
- 修复缺项或矛盾的 QA 结果被放行，以及浏览器检查不可用时以估算结果报告通过的问题。
- 修复画廊构建静默跳过非法模板或样例的问题，生成失败时终止发布。

### 升级说明

- 使用 `knowme forge --profile-json <file>` 提供结构化资料，继续兼容已有裸 profile JSON。当前流程不支持从项目仓库提取经历生成简历。
- 生成文件保存在 `workspace/runs/<runId>/`，请读取返回的 manifest 获取交付路径；需要指定副本位置时使用 `--output` 和 `--html-output`。
- 运行环境要求 Python 3.9+、Node.js 22.13+、项目声明的 npm 依赖及兼容的 Chromium 浏览器；`arial-unicode` 预设另需本地 Arial Unicode MS 字体。
- 每个 `.resume-page` 对应一张 A4 页，`--expected-pages` 设置一或二页的上限，两页布局需要显式页面容器。自动适配保留 8.8pt 最小正文字号，无法满足布局时会提示进一步调整。

### 已知问题

- 各平台安装流程尚未完全统一：部分适配器仅写入提示配置，复制的 Skill 包需另行准备运行依赖，安装器也可能在部分失败后提示完成。使用前请检查安装资源与依赖。自动 PDF 检查不保证所有 ATS 对多栏内容的阅读顺序解释一致。

---

## [0.0.5] - 2026-09-01

### 🚀 新增功能 (Added)
- **多模板全字段数据回填引擎 (`scripts/template/instantiate-resume.py`)**：
  - 深度升级 `render_profile_into_html`，打通 4 套不同几何结构模板（单栏、双栏侧边栏、顶栏双栏、结构化表格）的全字段自动化回填；
  - 覆盖个人基础信息 (`basics`：姓名、求职意向、联系电话、邮箱、城市、GitHub、个人摘要/核心价值定位)；
  - 覆盖专业技能矩阵 (`skills`：分类技能行、技能标签云、表格矩阵单元格)；
  - 覆盖工作经历 (`experience`：机构名称、岗位徽章、时间跨度、FAB 动词成果亮点)；
  - 覆盖核心项目 (`projects`：项目名、角色、技术栈标签、交付价值)；
  - 覆盖教育背景 (`education`：毕业院校、所学专业、学位、GPA、荣誉成果)。
- **管线自动模板智能选择集成 (`scripts/pipeline/forge.py`)**：
  - 移除 `--template` 参数的死板默认值，当用户未显式指定模板时，自动调用 `search-template.py` 的 Hybrid 混合评分引擎（70% 加权规则 + 30% BM25 文本相关度），基于目标岗位与候选人特征自动选择最优模板；
  - 显式传递 `--template` 参数时保留最高优先级覆盖。

### 🎨 视觉与样式优化 (Changed)
- **去 Emoji 化与商务极简视觉规范 (Formal & Clean Styling)**：
  - 全面清理所有模板（`minimal`, `modern`, `executive`, `classic`）中的 Emoji 图标（如 `📱`, `✉️`, `📍`, `🎓`, `🔗` 等）；
  - 统一采用简洁专业的文本标签（如 `.contact-label`、`.badge-label`、`.info-label`），右对齐或行内排布，杜绝视觉杂乱；
  - 移除 `executive` 顶栏多余的半透明气泡卡片边框背景，还原为清爽专业的 Hero Banner 联系人排布。
- **模板与生成器类名契约对齐**：
  - 在 `src/templates/modern/style.css`、`minimal/style.css`、`classic/style.css` 中补全运行时 HTML 生成器所需的全部类名样式（`.role-badge`, `.tech-tag`, `.tech-stack-tags`, `.sidebar-section`, `.experience-item`, `.project-item`, `.contact-label`, `.badge-label` 等）；
  - 在 `src/templates/common/base.css` 中正式确立 Instantiator HTML Contract 契约规范。

---

## [0.0.4] - 2026-08-28

### 🐛 缺陷修复 (Fixed)
- **CLI 选项与参数解析修复 (`cli/src/index.ts`)**：
  - 增加 `--version`、`-v` 与 `version` 命令分支处理，支持直接输出包版本号而非落入帮助菜单。
- **模板搜索引擎岗位参数兼容 (`scripts/template/search-template.py`)**：
  - 增加 `--role` / `-r` 命名选项支持，完美兼容 `knowme search --role "<岗位>"` 与 `knowme search "<岗位>"` 两种调用语法。

---

## [0.0.3] - 2026-08-28

### 🚀 新增功能 (Added)
- **4-Tier 渐进式文档金字塔工程 (Docs Engineering)**：
  - **L0 平台入口**：`SKILL.md` 统一 6 阶段确定性工作流契约；
  - **L1 行为与开发契约**：根目录新增 `AGENT.md`（全面吸收 Vercel Editorial 规范、优先级决断秩序、Four-Pass 严密工序、反模式黑名单与静默交付标准）+ `CLAUDE.md` 开发者速查；
  - **L2 架构与决策体系**：根目录新增 `ARCHITECTURE.md`（六层架构、端到端数据流、Deep Module Seam 设计）+ `docs/decisions/`（4 篇 ADR 架构决策记录）；
  - **L3 领域运行时规范**：归一化重构 `references/`（`01-evidence-mining.md` ~ `06-qa-and-rendering.md`），与 6 阶段保持 1:1 严格对齐。
- **两层 Design Tokens 架构与基础样式库 (`src/templates/common/base.css`)**：
  - 声明基础 Primitive Tokens（Slate/Blue/Teal/Navy 调色板、2pt 间距阶梯 `--primitive-space-1` ~ `--primitive-space-12`、A4 绝对打印契约 `@page` & `print-color-adjust`）；
  - 全量重构 4 套核心模板 `style.css`，由 Component Tokens 引用 Primitives，消除 60% 冗余代码；
  - `scripts/template/instantiate-resume.py` 自动合并内联 `base.css` + `style.css`，严格保证单文件自包含修改场铁律。
- **深模块化可插拔搜索引擎内核 (`scripts/template/search-template.py`)**：
  - 抽象 `BaseTemplateScorer` 策略接口，实现 `WeightedRuleScorer`（加权规则打分）、纯 Python 标准库 `BM25TextScorer`（全文相关度检索）与 `HybridTemplateScorer`（70% 规则 + 30% BM25）；
  - CLI 支持 `--engine hybrid|weighted|bm25` 自由切换。
- **架构决策记录 (ADRs in `docs/decisions/`)**：
  - `0001-html-intermediate-canvas.md`（HTML 作为唯一中间修改场）；
  - `0002-pure-css-design-tokens-over-tailwind.md`（纯 CSS3 变量替代 Tailwind 编译链）；
  - `0003-two-tier-tokens-architecture.md`（Primitive + Component 两层 Token 分层）；
  - `0004-decentralized-json-with-bm25-index.md`（去中心化 JSON 元数据 + 构建期 BM25 索引）。

### 🔄 优化与重构 (Changed)
- **平台适配器与分发打包机制**：
  - 同步更新 Cursor (`.mdc`)、Windsurf (`.rules`)、Claude Code (`.md`)、Codex (`.yaml`)，指向全新 `AGENT.md`、`ARCHITECTURE.md` 与 `references/01~06`；
  - 升级 `cli/src/commands/init.ts`，在执行 `knowme init` 时完整打包 `references/`、`AGENT.md` 与 `ARCHITECTURE.md`。
- **全链路自动化测试套件**：
  - 调整各测试用例以精确断言两层 Tokens、参考手册结构与检索门面，全量 24 项测试 100% 通过。

---

## [0.0.2] - 2026-08-26

### 🚀 新增功能 (Added)
- **代码仓与 Git 事实挖掘引擎 (`scripts/evidence/extract-evidence.py`)**：
  - 深度实现 `repo-to-resume` 核心引擎，自动解析本地工程的 `package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、Docker 容器配置、CI/CD 流水线与 Git 提交历史；
  - 自动评定生成可追溯的 **L1~L3 级证据链**，输出标准候选人事实底座档案 `workspace/evidence-master.json`。
- **候选人主档案 Schema 规范 (`src/knowledge/resume-schema.json`)**：
  - 定义形式化 JSON Schema 标准，严格规范基本信息、技能矩阵、工作经历、核心项目、教育背景与证据等级字段。
- **一键全流程装配管线 (`scripts/pipeline/forge.py`)**：
  - 提供单命令打通“代码挖掘 ➔ JD 解析 ➔ 模板匹配 ➔ HTML 画布装配 ➔ Dual QA 质检 ➔ A4 PDF 导出”的端到端管线；
  - CLI 同步支持：`knowme forge --repo . --role "<目标岗位>" --template modern --quiet`。
- **跨平台自愈式 PDF 渲染器 (`scripts/rendering/render-pdf.py`)**：
  - 实现多策略浏览器自动探测机制，自动嗅探并调度 Playwright Headless 或 macOS、Linux、Windows 上已安装的 Chromium、Google Chrome、Microsoft Edge、Brave 浏览器；
  - 彻底摆脱对特定操作系统硬编码路径的依赖。
- **领域模块化脚本架构体系 (Domain Architecture)**：
  - 全量将 `scripts/` 目录划分为 6 大高内聚子模块：`pipeline/`（管线）、`evidence/`（证据挖掘）、`template/`（模板装配）、`validation/`（双重质检）、`rendering/`（PDF渲染）与 `build/`（构建测试）；
  - 清理根目录下所有遗留脚本，实现纯净模块化切换。
- **脚本架构与 Agent 执行规范手册 (`scripts/Agent.md`)**：
  - 编写面向 AI Agent 与研发人员的权威规范文档，明确各模块职责边界、调用接口、自适应根路径解析与静默执行协议。
- **开源合规与第三方灵感溯源声明 (`THIRD_PARTY_NOTICES.md`)**：
  - 明确对 `repo-to-resume-tailor`、`ui-ux-pro-max-skill`、`ResumeSample`、`ResumeCollection` 优秀开源项目的致谢与架构溯源，声明系统字族合规性。
- **中间修改场结构化数据智能注入 (`scripts/template/instantiate-resume.py`)**：
  - 支持将 `evidence-master.json` 中的候选人事实数据直接注入 HTML 语义化节点，保留 Design Tokens 与关键词高亮。

### 🔄 优化与重构 (Changed)
- **Agent 静默交付协议与对话降噪 (Quiet Execution Protocol)**：
  - 在 `SKILL.md` 与 6 大平台配置文件（`agents/*`）中确立严格静默执行契约；
  - 严禁 Agent 在 Chat 对话框中打印数百行 HTML/CSS 或现场编写临时脚本；
  - 规范最终交付格式为：**核心价值定位 + Top 3 真实证据亮点 + 最终 PDF 产物路径**。
- **CLI 命令体系扩充 (`cli/src/index.ts`)**：
  - 新增 `knowme forge`、`knowme extract`、`knowme render` 命令，全量接入模块化子路径路由。
- **全链路自动化测试套件扩充 (`tests/`)**：
  - 扩充至 24 项端到端全覆盖测试，验证代码事实抽取、一键管线、模块路径与 Agent.md 规范。

### 🐛 缺陷修复 (Fixed)
- **修复跨平台 PDF 打印依赖**：消除了原先硬编码 macOS Chrome 路径导致的非 Mac 环境崩溃问题。
- **修复关键词嵌套双重加粗**：修复了 `instantiate-resume.py` 中正则表达式对已有 `<strong>` 重复包裹的语法瑕疵。
- **修复 Agent 空白占位符幻觉**：通过提供标准化事实提取与装配工具，杜绝了 AI 凭空编写《占位符》和现场造轮子的不稳定行为。

---

## [0.0.1] - 2026-08-20

### 🚀 初始版本 (Initial Release)
- **核心定位与 6 阶段确定性工作流**：
  - 确立 KnowMe CareerForge 核心范式：*Know Me (自我事实挖掘)* ➔ *Define (目标定位)* ➔ *Understand (JD解析)* ➔ *Position (策略映射)* ➔ *CareerForge (HTML修改场)* ➔ *Review & QA (双重质检与导出)*。
- **首期 4 套黄金基准 HTML5/CSS3 简历模板**：
  - `minimal`：后端/AI/系统研发高密度极简单栏模板；
  - `modern`：全栈/AI 现代深海蓝 32:68 双栏侧边栏模板；
  - `executive`：技术总监/架构师 33:67 深色顶栏领导力模板；
  - `classic`：政企/国企/综合类现代结构化高密度表格模板。
- **通用 HTML 简历契约规范 (`src/templates/common/resume-contract.md`)**：
  - 统一 DOM 语义化结构、CSS Design Tokens 变量体系与 A4 打印物理几何标准（`210mm x 297mm`，`1122.5px` 基准）。
- **9 大技术岗位画像结构化知识库 (`src/knowledge/roles/*.json`)**：
  - 涵盖 AI Agent 工程师、前端架构师、Java 后端、Node 全栈、Android、iOS、C++ 系统、架构师、产品经理。
- **多维加权打分搜索引擎 (`scripts/template/search-template.py`)**：
  - 综合岗位匹配度 (35%)、风格倾向 (25%)、ATS 评级 (20%)、页数 (10%) 与密度 (10%) 进行加权检索推荐。
- **双重 QA 自动化质检工具链**：
  - DOM 绝对高度溢出与孤行检测器 (`scripts/validation/validate-layout.ts` & `validate-resume.py`)；
  - ATS 纯文本可提取性与标头层级校验器 (`scripts/validation/validate-ats.ts`)。
- **静态交互式模板画廊生成器 (`scripts/build/build-gallery.py`)**：
  - 自动化构建生成 `output/templates_gallery/index.html` 实时 A4 预览画廊。
- **多 Agent 平台分发生态与统一 CLI**：
  - 统一元数据 `skill.json`；
  - 适配 Claude Code、Codex、Cursor (`.mdc`)、Windsurf (`.rules`)、Gemini CLI、OpenCode 等平台；
  - 全局 CLI 命令 `knowme`（支持 `init`、`list`、`search`、`validate`、`gallery`、`test`）。
