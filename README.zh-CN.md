<div align="center">

# 🎯 KnowMe CareerForge

<p align="center">
  <strong>认识自己，明确方向，锻造属于你的职业机会。</strong><br>
  <em>Know Yourself. Define Your Direction. Forge Your Opportunity.</em>
</p>

<p align="center">
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/语言-🇨🇳_简体中文-0284C7?style=flat" alt="简体中文"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/Language-🇺🇸_English-4F46E5?style=flat" alt="English"></a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/knowme-careerforge-skill"><img src="https://img.shields.io/npm/v/knowme-careerforge-skill?style=flat&logo=npm&logoColor=white&color=CB3837" alt="npm package"></a>
  <img src="https://img.shields.io/badge/Node.js-%3E%3D18-339933?style=flat&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-A4_PDF-2EAD33?style=flat&logo=playwright&logoColor=white" alt="Playwright">
  <a href="LICENSE"><img src="https://img.shields.io/badge/开源协议-MIT-6B7280?style=flat" alt="License: MIT"></a>
</p>

</div>
---

## 1. 什么是 KnowMe CareerForge？

**KnowMe CareerForge** 是一款专为 Claude Code、Cursor、Codex、Windsurf 及 Gemini CLI 打造的工业级、Agent-Native 简历工程 Skill。

传统的 AI 简历工具通常将写简历视为简单的“文本生成任务”：给大模型一段提示词，吐出一堆 Markdown，再经由黑盒转换器输出格式混乱、排版错位、充斥幻觉的 PDF。

**KnowMe CareerForge** 从底层重构了这一范式，打造为结构化的**双引擎协作系统**：

```text
knowme-careerforge-skill
          │
          ▼
   KnowMe CareerForge
          │
    ┌─────┴─────┐
    ▼           ▼
  KnowMe     CareerForge
    │           │
认识自己       锻造职业表达
真实经历与证据   工程化定制交付
```

- **KnowMe（自我认知与证据挖掘引擎）**：帮助候选人深入认知自我，系统梳理真实经历与可验证的代码/项目证据（L1~L3 分级），提炼真正具备竞争壁垒的优势点。
- **CareerForge（职业定位与简历工程引擎）**：将候选人的真实优势精准对齐目标岗位（JD），以 **HTML 中间工作区（Intermediate Canvas）** 与 **Design Tokens（设计系统变量）** 为工作场进行微调排版，最终通过 Playwright 无头浏览器导出确定性、像素级的矢量 PDF。

---

## 2. 核心价值观与设计原则

> ### *"目标不是让候选人看起来比真实情况更优秀，而是让真实的优势被正确的机会看见。"*
>
> *(The goal is not to make the candidate look better than they are. The goal is to make their real strengths visible to the right opportunity.)*

```text
【错误方向 (传统 AI 盲目夸大与幻觉)】
目标 JD ──> 提取关键词 ──> AI 凭空猜测 ──> 虚假包装 ──> 夸大造假 (面试必露馅)

【正确方向 (KnowMe CareerForge 证据为先)】
真实经历 ──> 代码/事实证据 ──> 核心优势 ──> 岗位精准匹配 ──> 高质量职业叙事与工程交付
```

---

## 3. 安装与部署指南

你可以通过 **CLI 极速初始化 (无需 Clone)** 或直接通过 **Agent 原生规则文件** 接入：

### 方式 A：通过 CLI 快速安装 (推荐)

直接使用 `npx` 免安装初始化：

```bash
# 进入你的目标项目目录
cd /path/to/your/project

# 为你所使用的 AI 编程助手一键安装 Skill
npx knowme-careerforge-skill init --ai cursor    # Cursor (.cursor/rules/)
npx knowme-careerforge-skill init --ai claude    # Claude Code (~/.claude/skills/)
npx knowme-careerforge-skill init --ai codex     # Codex CLI (~/.codex/skills/)
npx knowme-careerforge-skill init --ai windsurf  # Windsurf (.windsurfrules)
npx knowme-careerforge-skill init --ai gemini    # Gemini CLI (~/.gemini/skills/)
npx knowme-careerforge-skill init --ai opencode  # OpenCode (.opencode/skills/)
npx knowme-careerforge-skill init --all          # 为所有支持的平台一键安装
```

或全局安装 CLI：

```bash
npm install -g knowme-careerforge-skill
knowme init --ai cursor
knowme list
```

---

### 方式 B：Agent 平台原生手动配置

| 平台 | 目标注入路径 | 配置方法 |
| :--- | :--- | :--- |
| **Cursor** | `.cursor/rules/knowme-careerforge.mdc` | `cp SKILL.md .cursor/rules/knowme-careerforge.mdc` |
| **Claude Code** | `~/.claude/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.claude/skills/` |
| **Codex** | `~/.codex/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.codex/skills/` |
| **Windsurf** | `.windsurfrules` | `cat agents/windsurf/knowme-careerforge.rules >> .windsurfrules` |
| **OpenCode** | `.opencode/skills/knowme-careerforge/` | `cp -r knowme-careerforge-skill ~/.opencode/skills/` |

---

## 4. 三大运行模式 (Operational Modes)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 模式 A：目标岗位模式 (Target-Role Mode)                                       │
│ 用户指定职业发展方向（如“资深 AI Agent 研发工程师”）。                       │
│ ▶ Agent 加载岗位能力树，从经历库中提取强匹配证据，派生对应 Resume Variant。  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 模式 B：具体 JD 定制模式 (JD-Specific Mode)                                 │
│ 用户粘贴具体的招聘需求 (Job Description)。                                   │
│ ▶ Agent 运行 analyze-jd.py 执行差距分析，提取加分项并高亮核心招聘信号。     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 模式 C：代码库到经历挖掘模式 (Repo-to-Resume Mode)                           │
│ 用户提供 GitHub 仓库链接、代码目录或工程笔记。                              │
│ ▶ Agent 审查源码与配置文件，判定 L1~L3 证据等级，重塑为高质量 FAB 论据。    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 端到端执行工作流 (The 6-Stage Workflow)

```text
  Know (证据分级) ──> Define (明确目标) ──> Understand (洞察JD) ──> Position (制定策略) ──> Forge (HTML修改场) ──> Review (双重QA)
```

1. **[KnowMe] 证据挖掘**：分析候选人代码库与真实经历，严格划分为 L1 (代码配置直证)、L2 (模块依赖推断) 与 L3 (合理解读)。
2. **[Define & Understand] 信号提取**：解析目标 JD，提取必备项、加分项与团队招聘风格。
3. **[Position] 优势对齐**：差距分析匹配真实证据，规划模块优先级。
4. **[CareerForge] 模板检索与组装**：通过多维打分引擎检索最佳模板，实例化生成 `workspace/resume.html`。
5. **[Review & Dual QA] 闭环自愈**：无头浏览器检测 DOM 高度溢出与 ATS 文本流，自愈调校 CSS 间距 Tokens。
6. **[PDF Export] 确定性渲染**：通过 Playwright 导出无损矢量 `workspace/resume.pdf`。

---

## 6. CSS Design Tokens 调优与自愈速查表

所有排版参数均集中在 `workspace/resume.html` 的 `:root` 变量中，可进行全局即时微调：

| CSS Token 变量名 | 默认推荐值 | 紧凑模式 (单页微调) | 宽松模式 (双页饱满) | 调优核心作用 |
| :--- | :--- | :--- | :--- | :--- |
| `--resume-space-section` | `12pt` | `9.5pt` ~ `10.5pt` | `14pt` ~ `16pt` | 模块间纵向间距 (自愈核心旋钮) |
| `--resume-space-item` | `8pt` | `6.5pt` ~ `7pt` | `9pt` ~ `11pt` | 经历/项目条目间距 |
| `--resume-font-size-body` | `9.2pt` | `8.8pt` ~ `9.0pt` | `9.5pt` ~ `10pt` | 正文字号 (物理安全底线 8.8pt) |
| `--resume-line-height-body`| `1.45` | `1.38` | `1.50` | 正文行高比例 |
| `--resume-color-accent` | `#2563eb` | 自定义 Hex | 自定义 Hex | 主题强调色 (科技蓝/松石绿/经典深蓝) |
| `--resume-sidebar-width` | `32%` | `30%` | `35%` | 侧边栏占比 (双栏/高管模板有效) |

---

## 7. 首期 4 款黄金基准模板

| 模板 ID | 版式风格 | 岗位分类 | ATS 评级 | 适用人群与设计特质 | 目标页数 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`minimal`** | 单栏极简线性流 | 研发 / AI | Tier 1 (极佳) | 后端、算法、系统、AI 工程师；强调技术胶囊与代码证据 | 1 页 |
| **`modern`** | 左右双栏 (32:68) | 研发 / 全栈 | Tier 1 (极佳) | 全栈、AI 应用、海外远程；深海蓝侧栏，视觉层次丰满 | 1~2 页 |
| **`executive`** | 墨黑顶栏 + 33:67 双栏 | 管理 / 产品 | Tier 1 (极佳) | 技术总监、首席架构师、Team Lead；突出领导力与重大项目 | 1~2 页 |
| **`classic`** | 现代结构化表格网格 | 综合 / 政企 | Tier 1 (极佳) | 国企、金融科技、政企合规岗位；6列矩阵，最高信息密度 | 1 页 |

---

## 8. CLI 命令参考

```bash
# 1. 一键全流程装配管线（代码挖掘 -> HTML画布 -> 双重质检 -> A4 PDF）
knowme forge --repo . --role "AI Agent Engineer" --template modern --quiet

# 2. 智能检索最匹配的 HTML 简历模板（混合评分引擎）
knowme search --role "AI Agent Engineer" --engine hybrid

# 3. 深度抽取代码仓事实证据与可验证经历
knowme extract --repo . --output workspace/evidence-master.json

# 4. 运行布局结构、Design Tokens 与 ATS 双重质检
knowme validate

# 5. 确定性导出无损矢量 A4 PDF
knowme render --input workspace/resume.html --output output/resume.pdf

# 6. 编译生成可视化模板画廊
knowme gallery
```
---

## 自动化测试与持续集成

```bash
npm test
# 或:
python3 scripts/build/run-all-tests.py
```
---

## 10. NPM 构建、发布与版本更新

本项目已配置为标准的 NPM Package，支持一键编译、测试与发布：

```bash
# 1. 执行发布前自动化测试与打包预检
npm run release -- 0.0.4

# 2. 发布至公共 NPM 注册表
npm publish --access public
```

更多详细发版与 SemVer 版本升级策略请参阅 [NPM 构建与发布更新指南](docs/PUBLISHING.zh-CN.md)。

---

## 11. 开源协议

本项目采用 **MIT 开源协议**，详情请参阅 [LICENSE](LICENSE) 文件。
