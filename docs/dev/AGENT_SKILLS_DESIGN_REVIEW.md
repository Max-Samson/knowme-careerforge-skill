# Agent Skills 标准对照与项目设计评审

评审日期：2026-09-05。范围：`agentskills/agentskills` 的格式规范、创建与客户端指南、`skills-ref` 参考代码，以及本项目当前工作区。此报告区分标准合规、项目设计和未完成工程项；不是跨平台认证或完整安装测试报告。

## 1. 上游项目真正定义了什么

[上游仓库](https://github.com/agentskills/agentskills) 主要提供能力包格式、创作指南和参考工具。它不是简历引擎，也不规定本项目必须采用哪套应用架构。其模型是让宿主在需要时加载一组任务知识和工具，而非将所有规则永久放进上下文。

[格式规范](https://agentskills.io/specification) 规定 `SKILL.md` 与元数据；`scripts/`、`references/`、`assets/` 是资源组织惯例，额外目录允许存在。由此，本项目应修正入口和分发契约，而不是为迎合示例重命名全部模板与知识目录。

[客户端集成指南](https://agentskills.io/client-implementation/adding-skills-support) 讨论发现、激活和资源访问。这些由宿主负责；跨客户端目录惯例与具体平台配置不等于格式本身的强制要求。客户端可能宽容接收某些不规范输入，但作者侧不能依赖这种宽容声明合规。

[skills-ref README](https://github.com/agentskills/agentskills/blob/main/skills-ref/README.md) 明确该库是演示参考实现。其 [validator.py](https://github.com/agentskills/agentskills/blob/main/skills-ref/src/skills_ref/validator.py) 检查入口解析后的字段、名称及目录匹配；没有验证脚本依赖、模板资源可用性或执行质量。代码中 `validate_metadata` 未完整检查所有可选字段的类型，因此工具无报错也不能替代规范审阅。

## 2. 设计判断

### 2.1 保留的结构

现有 `SKILL.md → references/ → scripts/ + src/` 结构适合本项目。入口较短，工具处理容易产生错误的机械步骤，Agent 负责理解和表达，符合按需加载与职责分工。十套模板仍以 `canvas.html` 为唯一结构，标准不要求将其移入新建的 `assets/`。

开发说明和产品指令必须分离：`AGENTS.md` 引用开发正文 `AGENT.md`；`SKILL.md` 为用户制作简历。开发仓库包含 README、测试和 ADR 合理，不应因“保持 Skill 简洁”而删掉架构依据，也不应要求简历用户加载这些开发文件。

### 2.2 本轮入口修订

`SKILL.md` 描述增加实际适用请求：起草、岗位定制、修改已有画布和 PDF 导出。加入 MIT 许可证与确实存在的 Python、Node、npm、Chromium 和可选字体要求；正文增加项目开发请求的边界说明。用户已有流程与事实约束保持在原位置。

描述是否更准确触发需要宿主行为评估。本轮只验证字段和资源，不将文字修改直接等同于触发效果提升。[描述优化指南](https://agentskills.io/skill-creation/optimizing-descriptions) 将相关性判断作为需要测试的行为，而非靠增加关键词即可保证的属性。

### 2.3 控制强度按风险决定

对输入转义、归一化、错误状态、打印验收和发布使用确定性工具；对措辞、提问时机、模板选择保留合理判断空间。字体映射问题保留诊断与显式预设，不将某次模拟的字体强制用于所有平台。

依据 [创建实践](https://agentskills.io/skill-creation/best-practices)，维护重点是能改善决策的具体信息。新增规则需要对应真实失败，避免积累泛化口号。上游的入口长度建议不能用于要求开发手册同样缩短。

## 3. 当前项目对照与缺口

| 项目 | 当前证据 | 判断与后续验收 |
| --- | --- | --- |
| 标准入口 | 根目录 `SKILL.md` 有名称、描述与 metadata；本轮补 license/compatibility | 可进行字段检查；不代表安装包可运行 |
| 名称与目录 | 源码目录为 `knowme-careerforge-skill`，frontmatter 为 `knowme-careerforge`；完整安装分支目标同后者 | 对源码目录直接做严格目录匹配会失败；在命名正确的 staging 目录验收，不改产品名称或隐藏差异 |
| 分层加载 | 入口链接运行契约、模板选择、画布、QA | 保留直接路由；不把开发正文加载进简历流程 |
| 自定义清单 | `skill.json` 及 `agents/*` 自定义配置 | 本项目/平台扩展；包括 `$schema` 声明在内均不能作为上游通用规范依据，本轮未验证该 schema URL |
| 完整安装分支 | `cli/src/commands/init.ts` 的 Claude/Codex/OpenCode 分支复制 scripts/src/references 与入口 | 未复制 `package.json`、锁文件或 Node 依赖；浏览器引擎需要 Playwright、pdf-lib、pdfjs-dist。干净环境依赖准备不完整，是待修复工程项 |
| 提示配置分支 | Cursor/Windsurf/Gemini 分支只写配置，未复制完整运行资产 | 必须区分“提示配置完成”与“完整 Skill 安装”；当前缺乏工具包位置解析的端到端证明 |
| 安装失败状态 | `runInit` 捕获异常后继续循环，尾部始终报告完成 | 需增加每平台结果、非零失败退出和部分成功语义；该缺口未在本轮文档修改中修复 |
| 适配内容 | Gemini 文件仍使用旧六阶段表述；不同适配格式来自自定义约定 | 安装前统一引用现行入口，平台加载方式分别验证；不能据文件名认定原生支持 |
| 开发文档分发 | 安装器把 AGENT/ARCHITECTURE 也复制到运行目录，但不包含其全部开发引用 | 这些不是运行依赖；后续包清单应区分开发归档和运行包，不能要求消费者沿缺失开发链接执行 |
| 引用维护 | `references/` 与 `src/references/` 并存 | 运行入口以根 references 为准；兼容副本需要检查一致性，不能继续分叉 |
| 现有测试边界 | 测试覆盖模板、输入生命周期与浏览器 PDF 行为 | 源码运行回归不能证明安装包闭包或宿主触发准确性，需补独立安装与行为评估 |

这些判断来自源码审阅；本轮未对用户主目录执行 `knowme init --all`，也未声称已经重现每个平台的运行结果。

## 4. 目标分发边界

```text
开发仓库
  AGENTS.md → AGENT.md       开发入口与唯一规范正文
  ARCHITECTURE.md / docs/    架构与演进依据
  SKILL.md                  可分发产品入口
  references/               运行规则维护源
  scripts/                  确定性工具
  src/                      模板与知识资产
  package.json + lockfile   依赖声明
  agents/                   宿主适配资源
          ↓ 按安装清单暂存、验证
<temporary>/knowme-careerforge/
  SKILL.md + 完整运行资源 + 可复现依赖准备信息
          ↓ 在另一工作目录运行并验收
用户工作区中的隔离运行与产物
```

这是目标边界，不是本轮新增的打包器。后续实现应复用一份运行资产清单，避免各平台手写复制流程；与现有 CLI 兼容，先在临时目录验证，再处理真实安装。安装过程不应把开发 `AGENTS.md` 写到用户项目根目录。

## 5. 验收方案

### 格式与元数据

对 staging 中正确命名的 Skill 目录检查 YAML、字段类型/长度、名称匹配。可在隔离工具环境运行 `skills-ref validate <staged-skill-dir>`，记录工具来源版本。该命令需要额外安装参考库，不是本项目已提供的 npm 脚本。

### 包与命令

构建或安装测试禁止使用真实用户主目录。设置临时目标和外部工作目录，检查入口引用、Schema、完整 CSS、脚本及依赖准备资料。先测试稀疏 Draft，再测试浏览器可用时的最终 PDF；依赖缺失必须明确报告，安装器不得宣告完整就绪。通过源码树中的 `npm test` 只是其中一层。

### Agent 行为

根据 [评估指南](https://agentskills.io/skill-creation/evaluating-skills)，测试实际过程与输出，保留失败原因，不只匹配回答措辞。建议基线：

| 请求 | 预期行为 |
| --- | --- |
| 只提供少量经历，要求先做草稿 | 组织已知事实，不编造，允许 Draft |
| 提供旧简历和目标 JD | 保留事实，生成有来源关系的岗位版本 |
| 要求修改已有 HTML 的字号 | 保留当前画布编辑，不用旧资料重建覆盖 |
| 环境缺少浏览器或字体 | 明确不可验收，不交付旧 PDF |
| 解释本仓库模板目录或修改代码 | 进入开发上下文，不启动候选人信息采集 |
| 普通编程或与简历无关的问题 | 不因“项目”“技能”等关键词误启动简历流程 |

对入口描述或流程变更可比较改动前后在同组请求上的表现；不要把格式通过、工具回归通过和宿主效果通过混为一项。

## 6. 本轮变更范围与验证记录

本轮更新 `AGENT.md` 的包设计约束、`ARCHITECTURE.md` 的分发边界，并定点补充 `SKILL.md` 元数据与任务边界。未重构安装器、迁移模板目录、安装到真实宿主目录或发布包。

验证结果：

- 本地 skill-creator 的 `quick_validate.py` 返回失败：其字段白名单未包含官方已定义的 `compatibility`。这是校验器与标准的差异；保留有效字段，未修改或绕过该工具后声称其通过。
- 使用已安装 PyYAML 补充检查：字段白名单、名称格式、描述/环境声明长度、metadata 字符串类型与版本一致性通过。
- 在临时 `knowme-careerforge/` 目录检查名称匹配与入口直接链接通过；文档链接、代码围栏和 `git diff --check` 通过。这不是完整运行包测试。
- 本轮未运行 `skills-ref`，本机未安装该库；上游工具要求 Python 3.11+，应使用独立开发环境，不因此提高本产品 Python 3.9+ 的运行门槛。
- 未执行真实宿主触发评估或干净环境安装/PDF 测试。当前分发缺口保持为明确待实现项，不能标为已修复。
