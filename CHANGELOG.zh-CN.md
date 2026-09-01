# 更新日志 (Changelog)

**KnowMe CareerForge** 项目的所有重要版本演进与功能变更均记录于此文档。

本日志格式严格遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范，版本号遵守 [语义化版本 (Semantic Versioning)](https://semver.org/lang/zh-CN/) 标准。

---
## [0.0.6-planned] - 规划中 (Roadmap)

### 🚀 模板矩阵扩展 (方向二)
- 扩展 6 套核心新模板（`academic-research` 学术科研型、`international-flow` 欧美纯文字流、`creative-tech` 创意前端型、`compact-dense` 极致紧凑型、`startup-generalist` 初创全能型、`data-analyst` 指标看板型），达到 10 套黄金模板矩阵；
- 在 `base.css` 中引入 6 大主题调色板（Tech Blue, Deep Navy, Teal Modern, Emerald Fresh, Violet Creative, Slate Minimal），支持一键主题切换。

### 🛠️ 启发式 Token 自动自愈算法 (方向三)
- 在 `validate-resume.py` 与 `forge.py` 中内置 `--auto-heal` 闭环调谐算法（ADR-0005），根据 DOM 高度溢出阶梯式自动缩紧间距与字号，实现单次执行 100% 自动收敛。

### 💻 实时预览与交互建档向导 (方向四-1, 4-2)
- **本地实时热重载预览器 (`knowme preview` / `knowme serve`)**：基于标准库启动轻量 HTTP 服务并注入 SSE 监听脚本，在用户或 Agent 调整代码时实现浏览器秒级热更新（ADR-0006）；
- **交互式终端建档向导 (`knowme wizard`)**：为非代码仓用户提供流畅的 3-Turn 交互式提问采集，自动输出结构化 `evidence-master.json`。

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
