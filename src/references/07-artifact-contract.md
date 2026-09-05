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

## 每次运行独立

`forge --profile-json <file>` 在 `workspace/runs/<唯一运行ID>/` 下创建私有目录，包含 `input.json` 原始输入快照、`master.json`、`variant.json`、`resume.html`、`qa.json`、通过验收后写入的 `resume.pdf` 和 `manifest.json`。Draft 运行保存 `draft.json` 和草稿画布，不生成正式 PDF。

`--workspace` 仅改变运行目录的父目录，不复用已有运行。失败现场保留供诊断，不自动删除或继续使用其他运行的文件。目录包含个人资料，不提交到 Git；可由用户按需删除。测试必须使用临时目录。

`--html-output` 和 `--output` 是可选的已验收副本路径。先在独立运行中完成验证，再一起准备副本；写入失败时回滚普通错误，目标锁阻止两个本工具进程交错写入。跨文件复制不具备操作系统崩溃下的事务保证，因此运行目录和 manifest 始终是交付判据。发现遗留锁时报告冲突，不擅自删除其他运行的锁。

## 运行与检查状态

| status | 退出码 | 意义 |
| --- | --- | --- |
| RUNNING | 不作为最终结果 | 已开始但未完成，不能交付 |
| DRAFT | 0 | 草稿准备完成，无 PDF 验收承诺 |
| PASS | 0 | 本次指定检查及最终 PDF 验收通过 |
| FAIL | 1 | 输入、绑定、布局、PDF 内容或输出写入不符合要求 |
| UNVERIFIED | 2 | 浏览器、依赖、超时或检查协议故障，无法完成验收 |

`manifest.json` 包含 `runId`、`stage`、`errors`、`warnings`、`checks`、`outputs`。失败的 `outputs` 为空，即使目录或显式输出位置存在旧 PDF，也不能返回它作为本次交付。只有 PASS 的清单记录本次输出路径及 HTML/PDF SHA-256。JSON 模式与人读模式使用同一退出语义。

## 打印与最终 PDF

布局与导出共用 `scripts/rendering/browser-engine.js`，以 print 媒体模式等待字体，检查所有页面容器与内容边界。再生成新的 PDF，解析所有页，检查 A4 纵向尺寸、页数上限、逐页可提取文本与正文覆盖。最终写入的是通过验收的 PDF 字节，使用临时文件原子替换，不接受旧输出文件作为生成成功的证据。

自动调优不得增加当前间距，正文字号不降至 8.8pt 以下；调优失败保留原画布，不删改事实来强行过关。浏览器不可用不得用字数/盒模型估算替代 PASS。PDF 文本提取通过不代表所有 ATS 对多栏阅读顺序的解释一致；事实与视觉仍需 Agent 复核。

当前分页契约要求每个 `.resume-page` 对应一个 A4 页面，`--expected-pages` 为 1 或 2 的上限。一页文档可用上限 2；两页文档需由 Agent 显式建立两个页面容器。单个超高容器自然流入多页会被拒绝，不猜测浏览器分页后每页应有的内容。

输入文档的来源说明保存在 Master 的 source.suppliedSource 中，包括 synthetic-simulation 等原始标签。它是来源元数据，不是新增候选人事实。字体预设单独记录为 Variant.source.fontPreset；不得把字体修订误记为事实变更。
