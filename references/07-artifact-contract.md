# 资料、运行与验收契约

## Draft / Master / Variant

这三个值表示资料用途，不是质量评分，也不表示已独立核实事实。

| kind | 用途 | 约束 |
| --- | --- | --- |
| draft | 用户资料尚不完整的草稿 | 可缺姓名及经历；仅生成草稿画布，不能报告 PDF 已验收 |
| master | 用户或 Agent 整理的完整事实集合 | 每次运行只保存新快照，不反写输入；完整指保留本次已知事实，不强制具备所有可选字段 |
| variant | 为目标岗位派生的展示资料 | 记录来源 Master 的 profileSha256；岗位标题只修改 Variant，不回写 Master；不能作为下一份 Master 隐式导入 |

标准文档形状为：

```json
{
  "schemaVersion": "1.0",
  "kind": "master",
  "profile": {"basics": {"name": "候选人姓名"}},
  "source": {"type": "user-input"}
}
```

`profile` 的字段定义见 `src/knowledge/resume-schema.json`；脚本 `scripts/contracts/profile.py` 是归一化与封装契约的实现。脚本输出时附加 `profileSha256` 和 `missingFields`。摘要用于发现资料版本变化，不证明用户陈述真实性。手动修改封装资料后，应重新生成摘要或移除旧摘要再读入；不能保留不匹配的摘要。

兼容旧版的裸 profile JSON，按调用者明确提供的 Master 事实输入处理。封装为 Draft 的输入必须加 `--draft` 才能生成草稿；复核后由 Agent 显式整理为 Master，不由工具自动升级。Variant 的语义改写与事实选择仍由宿主 Agent 完成；当前脚本保留所有输入条目，只处理显式基础信息覆盖、岗位标题及展示装配。

## 缺失值

- 可选字段省略或 null 均表示未知，空白字符串归为 null，不生成占位候选人事实。
- null 的数组归为空数组；数组中的空白/null 项省略。未知字段和错误类型拒绝，不能悄悄丢失可能重要的资料。
- 教育经历、项目和工作经历为独立数组，按输入顺序完整处理；无教育描述不补“优秀毕业生”等默认荣誉。
- 缺失联系方式和目标岗位记录为待补信息。正式交付至少需要非空姓名及实质内容，打印与 PDF 验收进一步判断内容有效性。
- 旧版 L1/L2/L3 元数据可保留；用户陈述不因为来自对话就自动降级为“参与”。

## 独立运行与产物保留

运行隔离不等于永久保存每次运行。默认模式在系统私有临时目录中完成输入快照、Master/Variant、模板装配及完整 QA；正常成功或失败后清理本次临时目录。默认不会在用户目录创建 `workspace/`、隐藏事实档案或历史快照。

| 调用模式 | 用户目录新增产物 | 终端结果 |
| --- | --- | --- |
| 默认 `--profile-json -` | `resume/resume.html`、`resume/resume.pdf` | 简短报告，`retention: temporary`、`manifest: null`，仅当前交付路径及摘要 |
| 默认 `--draft` | `resume/draft.html` | DRAFT，仅 HTML，不修改已有 PDF |
| `--html-input -` | 验收后的当前 HTML/PDF 对 | 复用同一 QA 与发布机制，`templateUsed: existing-canvas`，不重建事实档案 |
| `--keep-workspace` | `workspace/runs/<runId>/` 完整归档 | `retention: archived`，默认完整报告；可用 `--summary` |
| 显式 `--workspace <dir>` | 指定父目录下的完整归档 | 保留原有归档行为，等同显式开启保留 |

`--profile-json` 接受已有文件或 `-`（从 stdin 读取 JSON）。`--html-input` 接受已有画布或 `-`（从 stdin 读取 HTML），与 profile 输入互斥；不能同时传岗位、模板、字体或基础字段覆盖参数，相关修改应先在画布中完成。文件输入只读；输出路径不得与输入文件冲突。为了更新同一份简历，读取当前 HTML 并在内存中修改后通过 stdin 提交，避免提前破坏当前交付。

默认输出可由 `--output`、`--html-output` 显式指定；只指定一项时，另一项使用相同主文件名与对应扩展名。归档模式不指定输出副本时，交付路径仍在归档目录。Draft 支持 `--html-output`，拒绝 PDF `--output`。

只有完成本次完整验收的 HTML/PDF 才一起准备发布；普通复制或替换失败回滚，目标锁阻止两个本工具进程交错写入。跨文件发布不具备操作系统崩溃下的事务保证。默认不读取旧文件判定成功，也不创建 `latest.json` 等额外成功标记；当前调用状态、输出路径及摘要是交付依据。不要擅自删除遗留锁。

归档模式保存原有输入、Master/Variant 或 Draft、HTML、QA、manifest 和通过验收的 PDF；HTML 输入不生成虚假的 Master/Variant，保存输入 HTML 与检查记录。失败现场仅在归档模式保留。纯净模式返回错误和必要诊断（含文本失败的缺字片段/码点、DOM 失败的页码/选择器/边界及 PDF 页数/尺寸；DOM 每类问题最多返回 20 条并附总数，不输出完整 DOM 正文），不返回已删除临时文件作为产物；需要深入诊断时显式保留下一次运行。进程被强制终止可能留下系统临时文件，不承诺强制终止时自动清理。

清理范围仅为本次工具创建的临时目录，不删除用户输入、旧版 `workspace/`、用户指定的记录文件或已有交付文件。目录中已有内容不会因升级而被“清空”。资料属于用户隐私，不提交到 Git。

## 运行与检查状态

| status | 退出码 | 意义 |
| --- | --- | --- |
| RUNNING | 不作为最终结果 | 已开始但未完成，不能交付 |
| DRAFT | 0 | 草稿准备完成，无 PDF 验收承诺 |
| PASS | 0 | 本次指定检查及最终 PDF 验收通过 |
| FAIL | 1 | 输入、绑定、布局、PDF 内容或输出写入不符合要求 |
| UNVERIFIED | 2 | 浏览器、依赖、超时或检查协议故障，无法完成验收 |

归档模式的 `manifest.json` 包含 `runId`、`stage`、`errors`、`warnings`、`checks`、`outputs`。失败的 `outputs` 为空，即使目录或显式输出位置存在旧 PDF，也不能返回它作为本次交付。PASS 报告记录本次 HTML/PDF 输出路径及 SHA-256；DRAFT 可记录 HTML 路径与摘要，但不表示 PDF 通过。JSON 模式与人读模式使用同一退出语义。

## 打印与最终 PDF

布局与导出共用 `scripts/rendering/browser-engine.js`，以 print 媒体模式等待字体，检查所有页面容器与内容边界。再生成新的 PDF，解析所有页，检查 A4 纵向尺寸、页数上限、逐页可提取文本与正文覆盖。最终写入的是通过验收的 PDF 字节，使用临时文件原子替换，不接受旧输出文件作为生成成功的证据。

自动调优不得增加当前间距，正文字号不降至 8.8pt 以下；调优失败保留原画布，不删改事实来强行过关。浏览器不可用不得用字数/盒模型估算替代 PASS。PDF 文本提取通过不代表所有 ATS 对多栏阅读顺序的解释一致；事实与视觉仍需 Agent 复核。

当前分页契约要求每个 `.resume-page` 对应一个 A4 页面，`--expected-pages` 为 1 或 2 的上限。一页文档可用上限 2；两页文档需由 Agent 显式建立两个页面容器。单个超高容器自然流入多页会被拒绝，不猜测浏览器分页后每页应有的内容。

输入文档的来源说明保存在 Master 的 source.suppliedSource 中，包括 synthetic-simulation 等原始标签。它是来源元数据，不是新增候选人事实。字体预设单独记录为 Variant.source.fontPreset；不得把字体修订误记为事实变更。

## 简短输入与交付入口

Agent 可直接整理裸 profile；只填写用户提供的值，删除未知字段及不需要的章节。以下尖括号仅说明字段含义，不能作为候选人数据执行：

```json
{
  "basics": {"name": "<用户姓名>", "title": "<目标岗位>"},
  "skills": [{"category": "<分组>", "items": ["<用户提供的技能>"]}],
  "experience": [{"company": "<公司>", "role": "<实际职务>",
    "startDate": "<开始时间>", "endDate": "<结束时间>",
    "bullets": [{"text": "<用户提供的职责或成果>"}]}],
  "education": [{"degree": "<学历>", "field": "<专业>"}]
}
```

姓名和至少一个实质章节是当前 PDF 输入门槛；联系方式、学校、专业和日期允许未知。`missingFields` 仅列出 basics.name/title/email/phone 的缺失，空列表不表示所有字段完整，更不证明事实真实。

默认纯净模式已经返回简短报告；`--summary` 在归档模式下精简终端报告。`--quiet` 只控制 JSON 格式，不决定是否留存文件。需要完整历史的旧调用应显式传 `--workspace` 或 `--keep-workspace`；没有这些参数的调用改为纯净输出，不再默认保存完整报告。失败的 outputs 始终为空，不能把路径下残留的旧 PDF 当成本次成功。
