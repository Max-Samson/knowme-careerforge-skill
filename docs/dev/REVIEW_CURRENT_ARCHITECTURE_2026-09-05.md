# KnowMe CareerForge 当前架构与功能实现审查

审查日期：2026-09-05。基线：HEAD `7cf8510` 加当前未提交及未跟踪的 v0.0.6 工作树。验收依据：README.md、RESUME_ENGINEERING_SKILL_DESIGN.md、ITERATION_PLAN_V0.0.6_EXPERIENCE_EXPANSION.md；同时核对 SKILL.md、CLAUDE.md、AGENT.md、ARCHITECTURE.md 与 ADR。

本次审查未修改实现或候选人资料。全量测试在临时副本运行；反例使用合成资料。上游项目的价值继承依据本项目文档判断，未进行上游源码逐项比较。P1 表示应在可靠交付前修复，P2 表示影响完整性、兼容性或可维护性。

## 0. 范围修正：以用户澄清的产品定位为准

用户在首次审查后明确：当前 Skill 主要依靠用户的信息输入和提示词描述，并未把“从项目仓库分析内容回填简历”作为已开发的产品功能。因此，本报告修订为以用户输入驱动、宿主 Agent 执行的 Skill 为审查对象。

首次审查误将 README 的仓库模式描述及现存脚本当作当前主使用流程，并由脚本缺乏语义策略推导产品能力不足。这两点判断撤回。脚本存在和可调用不能单独证明其属于当前产品范围；Agent 承担理解、访谈和岗位定制是本项目的正常架构，不要求为这些能力另建程序引擎。

本报告保留脚本复现记录，但明确适用条件：

- S1、S2 为非当前范围的仓库提取路径观察，不计入当前产品缺陷或修复优先级。
- S3–S6、S9–S11 是用户资料经 profile 实例化工具生成 HTML 时的缺陷，与资料是否来自仓库无关。Agent 直接编辑 HTML 时，不可据此断言同样缺陷必然发生。
- S7 是 JD 辅助脚本缺陷，不代表宿主 Agent 无法理解 JD；S8 收窄为可选 forge 自动路径与 Agent 语义结果的传递问题。
- QA、渲染与安装问题仍适用于调用相应工具的 Skill 流程。
- 尚未通过真实用户对话端到端评测访谈质量、事实整理质量和岗位定制质量，因此不对这些 Agent 能力作已失败结论。

## 1. 总体判断

项目定位和主要技术路线值得保留：真实经历与岗位定制相结合，结构化资料与模板分离，以自包含 HTML 为排版工作场，用 CSS Tokens 控制布局，用浏览器导出 PDF，适合作为宿主 Agent 的本地工具箱。

在用户输入驱动的定位下，架构可以成立：Skill 提供工作协议与知识资产，宿主 Agent 理解和组织用户经历，脚本辅助模板装配、排版检查和导出。现有复现说明部分辅助工具不能可靠保证资料保真与交付状态；这限制了工具层的可靠性交付承诺，但不能用这些脚本测试替代对整个 Agent 对话流程的评估。

KnowMe / CareerForge 可以作为两组职责组织：KnowMe 由提示词协议、访谈和知识参考引导 Agent 整理用户事实；CareerForge 由模板、Tokens 和工具帮助 Agent 完成交付。无需为两者建设同等数量的程序模块。主要应审查协议是否明确、上下文是否正确传递、工具是否保真，以及最终产物能否通过验收。

## 2. 设计层评估

### 值得保留的部分

- `scripts/evidence`、`template`、`validation`、`rendering`、`pipeline`、`build` 的职责分组清晰，不需要推翻目录重建。
- `src/templates/{id}/` 模板包与 `common/base.css` 的分层便于资产分发和统一调整。
- JSON 知识库规模较小，本地检索足以支撑当前 10 套模板；暂无必要增加服务端、向量数据库或复杂框架。
- 浏览器直接处理 HTML/CSS，减少文档格式转换环节。需要补充的是共享测量环境和最终 PDF 验收。
- 用户自然语言输入是主入口；`--profile-json` 可作为 Agent 整理资料后调用装配工具的内部接口，不要求用户自行提供 JSON。

### 需要修改的架构边界

1. **明确宿主 Agent 与脚本的职责。** Agent 负责识别意图、渐进追问、整理事实、理解 JD、岗位定制和内容改写。脚本负责其所承诺的字段绑定、输入检查、错误状态、测量与导出。事实是否超出用户表述需要在 Skill 的内容复核协议中约束，不能声称仅靠 schema 或布局脚本就能保证。
2. **区分用户事实与简历表达。** 保留用户已确认事实和目标约束，允许 Agent 针对岗位调整选择、顺序和措辞。可以先用一份轻量资料文件和策略备注实现；独立 Master/Variant schema 是多版本管理需要出现后的演进选项，不是当前 Skill 必须增加的架构。
3. **区分用户明确陈述与 Agent 推断。** 用户明确说“我负责该项目”，不应仅因来自聊天就自动改成“参与”；Agent 自行补出的职责或数字则必须追问或删除。来源、是否已确认、是否可外部核验可以分别记录，不宜把用户自述与上下文猜测统一当作弱推论。仓库贡献归属不属于当前必做范围。
4. **用明确状态代替笼统 SUCCESS。** 缺资料、待确认、布局未测、浏览器不可用、事实检查失败、PDF 验收通过应可区分。启发式估算不能升级为已验证通过。
5. **确定性需要环境边界。** 系统字体栈、任意系统 Chrome 与多种后备渲染方式意味着环境会变化。建议承诺固定浏览器/字体环境下的可重复布局，并记录渲染环境；现有配置不足以证明跨平台像素一致。
6. **统一分页模型。** HTML 契约说每个 `.resume-page` 是一张 A4，自愈却使用首个容器高度对比 `页数×1122.5`。显式多页容器与连续流分页需要分别处理，最终以 PDF 页数验收。

建议数据流：

```text
用户描述 / 已有资料 / 目标岗位或 JD
  → Agent 识别意图、必要追问、整理已确认事实
  → Agent 借助知识库完成岗位定制和内容组织
  → 选择模板、写入或编辑 HTML、调整 Tokens
  → 对照用户资料复核内容 + 工具检查打印布局
  → PDF 导出及页数/文本验收 → 交付
```

## 3. Spec：事实、内容与岗位定制

### S1 / 范围外观察：依赖、空目录被升级为候选人的 L1 成就

位置：`scripts/evidence/extract-evidence.py:198`、`:295`、`:344`。

复现仓库只有 `package.json` 的 Prisma 依赖和空 `tests/` 目录，输出却包括 PostgreSQL“高可靠端到端业务流”、主导测试体系、“核心负责人 / 主力开发者”以及“主导过多个核心系统”。依赖不能证明数据库选择、实际实现、效果或个人职责。空目录不能证明测试落地。

应输出可核查观察，如“依赖清单包含 Prisma”，将实现存在性、实际使用情况、效果和个人职责作为不同证据问题；不足时进入待确认，不能直接构造履历成就。

### S2 / 范围外观察：整个仓库提交数被归到当前用户

位置：`scripts/evidence/extract-evidence.py:80`、`:216`。

临时仓库全部 11 次提交由 Other Author 创建、本机 Git 身份为 Local Candidate，没有版本标签，仍输出候选人“累计提交 11 次代码并完成多版本发布”。Git 本地配置不是贡献证明，总提交数也不证明重构和发布。

应要求明确作者映射，分别统计候选人提交、仓库提交、发布证据；缺少映射时不得认领仓库成果。

### S3 / P1：模板样例事实泄漏到候选人简历

位置：`scripts/template/instantiate-resume.py:85`、`:132`、`:264`；`src/templates/modern/template.html:22`、`src/templates/data-analyst/template.html:26`。

空 experience/education/skills 不触发替换，示例学校、公司、技能和证书留在输出。完整 profile 下，modern 仍保留未绑定技能及 AWS 证书；data-analyst 保留 `+34.5%`、`1.2亿+`、`¥1800万` 等样例指标。

运行模板应只包含结构与占位绑定，展示资料另存 gallery fixture。字段缺失时删除对应区域或返回待补充；不能把“不替换示例”等同于“不编造”。

### S4 / P1：新增模板的教育回填覆盖真实工作经历

位置：`scripts/template/instantiate-resume.py:293`。

creative-tech 和 data-analyst 的教育标题为 `div.sidebar-title`，回填正则却向后寻找 h2。跨行匹配穿过教育 section，捕获后方工作经历标题，随后用教育数据替换工作正文。已复现真实公司和工作内容消失，学校出现在“工作经历”下方。

应按明确、唯一的 section 节点绑定并校验匹配数量，禁止依赖可跨节点边界的正则。新增模板必须跑同一真实 profile 的字段往返测试。

### S5 / P1：缺少荣誉时自动补“统招全日制 · 优秀毕业生”

位置：`scripts/template/instantiate-resume.py:274–278`。

没有 GPA 和非标准 summary 字段时强制加入该描述，9 套模板复现。标准 honors 没有用于该逻辑。两项都是需要用户确认的事实，应彻底删除此默认值。

### S6 / P1：profile 失败被当成装配成功

位置：`scripts/template/instantiate-resume.py:381–397`。

无效 JSON、`bullets: null`、姓名中的字面反斜杠触发注入异常后，只输出 Warning，然后保存整份原始样例并退出 0。显式提供不存在的 profile 路径也未失败。调用方 `check=True` 因而无法阻止交付。

显式 profile 必须成功校验和完整绑定才能提交输出。失败应非零退出，不覆盖已有画布；样例生成必须是显式 demo/gallery 路径。

### S7 / P2：JD 技能分类并未解析招聘要求

位置：`scripts/evidence/analyze-jd.py:32–37`。

- `熟练掌握Python，必须熟悉React和Docker。` 得到空技能数组：正则 `\w` 包含汉字，边界不适合中英文混排。
- JD 明确要求 Kubernetes，Python/TypeScript/JavaScript/Java/Go/Rust 都是加分，输出却将前六项归为必备、Kubernetes 归为加分。实现按词表顺序切前六项，未分析要求语义。

若保持轻量抽取器定位，应返回技能出现位置和原句，把未经确定的 requirement 分类交给 Agent；不能返回伪确定的 Must/Nice 结论。

### S8 / 条件性工具缺口：forge 未完整传递 Agent 的岗位选择

位置：`scripts/pipeline/forge.py:43–57`、`:96–134`。

选模发生在 JD 分析之前，未传关键词；只传 JD 时以 fullstack engineer 默认值选模。后续 JD 主要转化为最多八个高亮词，没有持久化的能力缺口、选用证据、经历排序或 Variant。Mode D 的 --role 没有进入已提供 profile 的标题回填。

以上只能说明该自动管线自身不完成完整岗位策略，不能据此否定 Skill 的岗位定制能力：宿主 Agent 可以先理解 JD、改写 profile、明确选择模板，再调用工具，或直接编辑 HTML。应在协议中明确传递目标标题、内容选择和模板参数；独立 requirements/evidence-map/variant 文件并非必须。

### S9 / P2：Schema 与缺失值约定冲突

位置：`src/knowledge/resume-schema.json:6`、`:10`、`:71`；`SKILL.md:121`。

SKILL 允许用户尚未提供的字段 null 或省略；schema 却要求姓名、标题、邮箱、电话全为字符串。该矛盾会直接影响 Agent 从用户描述整理出的资料；消费端没有 schema 校验。另观察到仓库生成器也不遵守 schema，但其输出不作为当前主流程验收依据。

建议明确采集阶段允许缺失、生成阶段哪些字段必需，以及空值的显示方式；集中实现装配接口输入检查。无需立即增加多个 schema，更不能为了通过 schema 自动造值。

### S10 / P2：合法字段和多段经历丢失

位置：`scripts/template/instantiate-resume.py:174`、`:266`。

10 套模板只读取 education[0]；field、honors、certifications 的复现值未被输出。Executive 项目处理嵌在非空 experience 分支下，无任职经历但有项目时项目丢失。

应让模板声明支持的 section/字段；截断必须属于显式 Variant 策略，有选择理由，不能隐藏在模板回填代码中。

### S11 / P2：联系方式依赖样例文本，文本未转义

位置：`scripts/template/instantiate-resume.py:71–82`、`:138`。

international-flow 中 `139-1234-5678`、Shanghai / Remote 不能被给定电话和成都替换；其他多个新增模板也保留样例城市。`vector<T>` 被直接拼入 HTML，会把 `<T>` 当成标签。

联系方式应按字段节点替换，文本先 HTML escape，再插入受控高亮。需要涵盖中英文、反斜杠、尖括号和空字段的测试。

## 4. Spec：QA、自愈与交付

### Q1 / P1：默认管线没有执行所宣称的 Dual QA

位置：`scripts/pipeline/forge.py:140–156`；`scripts/validation/validate-resume.py:273–336`。

forge 只调用轻量 Python validator，未调用 validate-layout.ts 和 validate-ats.ts。未开启 auto-heal 时无真实布局测量。空姓名、无正文、5000px 高度的 HTML 复现为 PASS；随后管线声称 Dual QA Passed 100%。

必须统一真实 QA 入口，将事实、HTML/ATS、打印布局和最终 PDF 检查结果分别报告，不允许以“脚本退出 0”代替完整验收。

### Q2 / P1：浏览器不可用时用估算冒充 DOM 验证

位置：`scripts/validation/validate-resume.py:75–101`。

Node/Playwright 不可用、浏览器启动失败、超时时静默退到字符数公式。模拟浏览器不可用，5000px 固定高度页面得到 617.7px，返回 healed=true、dom_height_px 和 PASS。

估算可作为排版建议，必须返回 measurementSource=estimate 与未验证状态；交付门禁需要真实测量，不能放行。

### Q3 / P1：只测第一个容器，且用屏幕样式判断打印结果

位置：`scripts/validation/measure-dom.js:76–89`。

真实 Chromium 复现：

| 反例 | 项目校验结果（要求1页、auto-heal） | 实际 PDF |
|---|---|---|
| 两个显式 A4 .resume-page 容器 | PASS，测得45px | 2页 |
| 屏幕块高100px，打印块高1500px | PASS，测得208px | 2页 |

实现 querySelector 只取首个容器，并去掉其高度约束；没有 emulateMedia(print)。应遍历页面、检查可见内容边界、水平溢出和实际 PDF 页数。内容自然高度可作调参输入，不能替代交付几何。

### Q4 / P1：系统浏览器失败时，旧 PDF 被误认为本次成功

位置：`scripts/rendering/render-pdf.py:101–102`。

已有旧 PDF，浏览器替换为 `/usr/bin/false`，函数仍返回 True。实现忽略进程退出码，只检查目标文件存在且非空。

应输出到本次唯一临时文件，验证进程退出、文件结构、页数与正文后原子替换最终文件。失败保留旧版本，但不得标记本次成功。

### Q5 / P2：JSON 模式的失败退出码错误

位置：`scripts/validation/validate-resume.py:358–360`。

JSON status=FAIL 后直接 return，进程退出 0。使用 HTML `<html></html>` 已复现。所有输出格式必须共享同一退出状态。

### Q6 / P2：自愈阶梯不保证单调收缩

位置：`scripts/validation/validate-resume.py:166` 起；`src/templates/classic/style.css:29–31`。

自愈从固定 10.5/9.5/8.5pt 开始，但 classic 原 section=6pt、item=4.5pt，可能越调越松。每次调整都重新启动浏览器；不能据此保证 ADR 所写的 <0.5 秒。

从 computed style 当前值生成候选，限定不扩大与最小可读值，保留最优状态；一次浏览器会话内迭代。目标函数还应包括可读性和是否丢失内容。

## 5. Standards：分发、CLI 与工程契约

### D1 / P1：发布包遗漏安装器必需资产

位置：`package.json:9–16`；`cli/src/commands/init.ts:125–128`。

npm files 清单没有 references/、AGENT.md、ARCHITECTURE.md；Claude/Codex/OpenCode 的安装器却需要复制这些文件。按清单在临时目录模拟发布包，OpenCode 初始化在复制 AGENT.md 时 ENOENT。仓库克隆可用不能证明免克隆安装可用。

应以真实 npm pack 产物在空目录验证安装，确保 SKILL 引用的资源、脚本与模板全部可达。该复现为按清单模拟，并非本次重新发布或从 npm 下载线上包。

### D2 / P1：CLI 丢弃失败状态，安装失败仍宣布完成

位置：`cli/src/index.ts:128`、`:135`、`:141`、`:147`；`cli/src/commands/init.ts:136–142`。

search/validate/gallery/test 未检查 spawnSync status/error；安装器 catch 错误后继续，最终无条件输出 setup complete。非法搜索参数、校验失败与安装异常均可被外层报告为成功。

应统一进程调用封装和错误模型；--all 应列出各平台结果，任一必要安装失败则总状态失败。不能让 Agent 从退出0推导环境已准备好。

### D3 / P1：规则已安装，规则引用的工具链未安装

位置：`cli/src/commands/init.ts:97–117`；`agents/cursor/knowme-careerforge.mdc:10`。

Cursor/Windsurf 只写规则，规则却调用用户当前项目下的 scripts/ 与 references/；在空项目初始化后这些资产不存在。Gemini 只安装 JSON，其中声明 SKILL.md entrypoint，但安装器没有复制该入口。

应统一部署完整运行资产，再为各平台生成指向实际安装位置的薄适配器。该判断仅基于项目内部路径契约，不涉及外部平台最新格式兼容性的推测。

### Source of Truth 与维护性判断

这些属于架构判断，不与可复现功能缺陷混为一类：

- README/SKILL/CLI 当前仍把仓库提取作为显著入口，与用户明确的当前范围不同。应将用户输入和提示词驱动流程置于首位，仓库模式明确标为未支持或实验性；不应让宿主 Agent 默认扫描当前项目。此次只修订审查报告，未擅自更改产品文档或功能。

- 根 references/ 与 src/references/ 存在重复资产路径；SKILL、架构说明、安装器和测试使用的位置不一致，应保留一个源并生成其他副本。
- README 的 Mode A/C 与 SKILL 的 Repo/Target-Role 编号对调；新旧模板数、路径及参数示例存在漂移。建议用能力清单和运行时schema生成帮助，文档描述职责，不重复实现细节。
- get_project_root、脚本回退路径、浏览器发现与命令执行多处重复。真正需要抽取的是稳定的 runtime/paths/process/renderer 边界，而不是为每份脚本增加一层只转发的类。
- 实例化器靠模板特定的 if 与正则识别布局，新增模板要求回查多处条件，是实际触发缺陷的修改分散问题。明确slot/field契约可以保留10套CSS，同时减少回填分支。
- Playwright、ts-node、TypeScript 仅列在 devDependencies，Python运行时又调用 npx ts-node 执行源码。生产安装后的默认依赖与执行入口需统一；浏览器后备方案不能替代打包环境验收。

## 6. 迭代计划完成度

| 交付项 | 当前状态 | 验收差距 |
|---|---|---|
| 6新增模板，合计10套 | 资产已存在，登记与画廊测试通过 | 内容绑定与事实保真未通过；不能按文件数验收 |
| 6套 palette | base.css已定义，搜索返回推荐 | 从推荐到最终画布应用需要闭环 |
| auto-heal独立与管线参数 | 已实现 | 测量来源、打印样式、多页、真实收敛边界不足 |
| knowme preview | 当前未实现 | preview-server.py、preview.ts缺失 |
| knowme wizard | 当前未实现 | wizard.ts和命令入口缺失 |
| 用户输入与渐进采集（现有文档称Mode D） | 已有完整问卷与profile入口，应按主流程定位 | SKILL仍强制首次整表，未落实三轮协议；未实际评测Agent会话 |
| 35+测试 | 当前30项 | 不能用增补浅层断言完成验收 |

这是迭代中的未完成项，不应把计划中的全部工作解释为已发布功能，也不能仅凭目前缺失判断排期失败。

## 7. 测试结果与覆盖缺口

- 全量 unittest 在临时副本：30项，29通过、1失败、0跳过。失败为 forge PDF 渲染：本地缺项目 Node 依赖，沙箱内系统浏览器启动受限。此结果不等同于发现一个确定的渲染代码回归。
- 允许启动临时浏览器并使用 Codex 自带 Playwright 后，6项自愈测试全部通过。
- 上述两份分页反例已用真实 Chromium 导出，并用 PDF 解析器确认各2页；项目校验器均 PASS。
- TypeScript noEmit 检查未执行成功：工作树没有 node_modules/.bin/tsc。不应声称编译通过。
- 实例化失败、伪造事实、JD错误分类、旧PDF成功误报和JSON退出码均有最小复现。

现有测试主要验证结构存在、命令成功和少量正向样例。自愈“收敛”测试允许 stage=none，没有断言初始确有 +5~+40px 溢出；字号测试仅当匹配字面 pt 时断言，没有保证走到字号阶段；内容建议测试直接调用 advisory 构造器，没有验证不可收敛流程。

测试本身也有副作用：`tests/rendering/test_smoke.py:118` 的 forge 使用固定 workspace/evidence-master.json；build-knowledge 测试回写索引。建议所有测试使用独立工作区，构建测试比对临时产物。

首批应增加的验收用例：用户仅输入一句职业描述时有针对性追问；已提供的信息不重复追问；明确自述与推断区分；目标岗位已给但无JD仍能继续；用户修改某项事实后最终简历正确更新；空资料不泄漏样例；坏JSON非零退出且保留原画布；10模板一致保留输入事实；多段教育；调用JD脚本时的中英文识别与要求分类；浏览器缺失返回未验证；真实打印2页拒绝1页交付；旧PDF不算新成功；CLI安装后的实际调用。对话协议需单独做真实宿主Agent或可复现的会话评测，不能只检查SKILL.md文本存在。

## 8. 按当前 Skill 定位修订的实施顺序

1. **对齐主入口与职责。** 用户信息输入和提示词为主流程；SKILL明确理解、追问、岗位定制、模板编辑和交付步骤，README/CLI避免引导未支持的仓库路径。现有Mode D不应被描述为边缘补充场景。
2. **优先改善采集与内容复核协议。** 先利用用户已提供的信息，按缺口渐进追问；确认事实、推断和待补充项分开；清楚规定内容编辑与直接HTML编辑的边界。
3. **修复主流程会调用的装配工具。** 清除事实默认值、隔离gallery样例、修复跨section覆盖和字段遗漏、统一空值规则、保证失败不覆盖有效产物。
4. **修复共用安装与交付工具。** 完整部署Skill依赖资产，正确传播错误；打印模式测量、实际PDF页数与文本验收；估算不得当作已验证，旧PDF不得当作本次成功。
5. **补充真实对话评测与体验功能。** 以简略描述、详细经历、已有简历、目标岗位、具体JD、后续修改等场景验证Agent使用Skill的全过程；再按迭代计划完成preview、wizard和palette应用。

不要求当前开发仓库解析器、独立语义推理服务或复杂EvidenceMap引擎。结构化事实记录是帮助Agent稳定执行的轻量机制，是否扩展Master/Variant文件体系由实际多版本需求决定。

原报告“Spec 17组、Standards 3组”的统计不再作为当前产品缺陷总数。S1/S2已移出当前范围，S8改为条件性工具缺口；其余脚本发现保留各自触发条件。整个Skill的对话质量与岗位定制能力仍待会话级验证，不能由单个脚本的能力边界推断。
