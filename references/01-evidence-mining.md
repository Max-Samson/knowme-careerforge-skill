# Expand supplied experience into strong resume content

Read this when composing or materially rewriting candidate content. Compare with the user's original messages or supplied resume, not just an Agent-generated profile. Tools verify that profile text survives rendering; they cannot establish that the profile was faithful in the first place.

## Compose, then check against the source

1. Identify supplied facts and the target role separately. Treat role/JD knowledge as requirements to compare, not personal qualifications. Use a relevant role profile when it helps expose an ability already supported by the material; skip it for a straightforward wording or contact edit.
2. Write a concise draft of the content. Every skill, responsibility, mechanism, result and level of proficiency must be supported by supplied material. Professional editing can improve order and clarity without increasing ownership, scope or certainty.
3. Before saving the profile, compare the claims with the original source. Remove unsupported additions; ask when a consequential ambiguity affects correctness or when a focused answer would materially improve the strongest evidence; otherwise deliver the supported draft. Keep this comparison internal, without a separate report or approval round. If helpful for a nontrivial rewrite, the existing bullet `evidenceSource` string can record a short source quotation; it is not printed and is not an independent verification claim.

Check each changed dimension: **technology · ownership · scope · mechanism · result · certainty**. A target title can go in the job objective; it cannot change an actual employment title, create years of experience in another stack, or become an item in skills.

## Expand meaning, not the candidate's history

The Agent is an editor and reasoning partner. Do more than copy the input: organize scattered facts, resolve supplied relationships, explain what an action demonstrates, and make the strongest evidence easy to read. More words are useful only when they add supported meaning.

Distinguish three operations:

| Operation | Treatment |
| --- | --- |
| Professional expression | Freely improve sentence structure, terminology, grouping and emphasis while preserving meaning. |
| Supported ability synthesis | Name a bounded ability demonstrated by the described action. Implementing an API can support “API development experience”; it does not establish distributed architecture expertise. Avoid “expert”, “proficient” or broad mastery without corresponding input. |
| New historical detail | Ask or present it as an optional question outside the resume. Do not assert an unprovided implementation, business setting, ownership, scale, result or metric. |

Use any suitable writing pattern, leaving unsupported parts out:

- **Delivery:** supplied responsibility + object/module + supplied implementation or collaboration context.
- **Problem solving:** supplied problem + personal action + known mechanism + observed result, if available.
- **Technical practice:** supplied technology + actual use + demonstrated, bounded capability.
- **Transferable ability:** concrete action + underlying problem-solving ability relevant to the target, without relabeling the original stack.
- **Leadership:** actual decision/coordination scope + personal action + supplied outcome. Seniority and target titles do not supply leadership evidence.

Do not fill every slot or force every bullet into FAB. Split a dense description when it contains distinct contributions; combine fragments when they describe the same achievement. Skills should summarize practice at the supported level, not become a catalog of the role profile.

### Examples: input → useful expansion

These examples illustrate reasoning, not reusable candidate facts.

- Input: “用 Node.js/NestJS 写了订单创建和状态查询接口。”
  Resume: “基于 Node.js / NestJS 开发订单创建与状态查询接口。”
  The input is already specific: a shorter sentence is better than adding “完成后端接口开发” to repeat it. Ability summary, if useful elsewhere: “具备 Node.js / NestJS 后端接口开发经验。” Prefer the concrete bullet when space is limited; do not repeat both mechanically. Do not add payment consistency, high concurrency or independent ownership.
- Input: “用 Python 做了内部文档问答，文档向量化后检索，再交给大模型回答。”
  Resume: “使用 Python 实现内部文档问答，将文档向量化、相关内容检索与大模型回答生成串联为 RAG 问答流程。”
  This names a mechanism the user actually described. It does not establish LangChain, a particular vector database, reranking, agent planning or production scale.
- Input: “参与 Redis 缓存开发，把热点商品信息放缓存，减少重复查数据库。”
  Resume: “参与商品信息缓存开发，使用 Redis 缓存热点商品数据，减少重复数据库查询。”
  Do not add cache-hit rate, distributed locks, cache penetration protection or a percentage improvement.
- Input: “做过 Agent，用过 LangGraph。”
  Safe current version: “具有基于 LangGraph 的 Agent 开发经历。”
  High-value question: “这个 Agent 完成什么任务？你实现了哪些节点、工具或流程？” Do not expand into multi-agent orchestration or autonomous planning without an answer.

## Ask for information that changes the writing

Prefer a focused question about the strongest relevant experience: what problem, what personal contribution, what concrete method, what observable change? Select the missing dimension with the highest value; do not require a fixed interview sequence or numeric results. User feedback, completed delivery, reduced manual work or resolved failures can be useful outcomes when supplied.

If the user wants an immediate result, write the supported version now and optionally mention the most valuable missing detail. If the user wants deeper expansion, use their answer to strengthen the draft. Do not block usable content on optional details or put unconfirmed placeholders into the final resume. Ambiguous ownership or conflicting critical facts warrant clarification; routine phrasing does not require approval.

## Concrete rewrite boundaries

These are isolated editing examples, not candidate material or a profile to execute.

| Supplied statement | Faithful treatment | Unsupported addition |
| --- | --- | --- |
| Worked with Node.js and NestJS; wants a Java role | Keep the actual stack; use Java only in the target title until the user supplies Java skills | Add Java/Git to skills, or describe the period as Java experience |
| Participated in Redis and message-queue work | Keep “participated” and the unnamed message queue | Led architecture; Kafka/RocketMQ; cache prewarming; payment/event pipelines |
| Optimized queries; response time decreased about 40% under high concurrency | Retain that result and its qualification in the strongest relevant work bullet | Average/P99, 20ms, QPS, indexing or SQL execution-plan changes not supplied |
| Developed order, user and payment modules | Describe the modules in the work entry | Invent a separately named high-concurrency project, new project dates or a “core owner” role |
| Used Spring Boot and MySQL | List those technologies or the supplied use case | Expert JVM/JUC knowledge, deep index internals, distributed transactions |
| Bachelor degree and a major, without school/dates | Include the two known education fields; omit unknown fields | Guess a university, dates, GPA or claim that all education data is complete |

Do not turn a suggested outcome into a required ingredient of every bullet. A duty without a metric remains valid. One supplied project can be developed into a project entry when actual context and contributions are available; do not duplicate the same work as a second achievement just to fill a section. Keep a brief summary distinct from detailed work bullets.

## Editorial review: make each sentence earn its place

Use these criteria to revise a substantive draft, not as a mandatory user-visible checklist or a fixed number of revision passes. Stop when the material is clear, useful and faithful; do not rewrite repeatedly for synonyms.

| Question | Editing action |
| --- | --- |
| What new information does the added phrase convey? | Remove restatements such as “开发接口，完成接口开发工作” and generic claims such as “展现优秀技术能力”. |
| Can a reader identify the candidate's action? | Prefer a concrete action and object to “深度赋能 / 全面推动 / 闭环落地”. Preserve the supplied ownership level. |
| Are method and result actually connected in the source? | Combine related facts, but do not attach a team's result to the candidate's action without support. |
| Does a number retain its meaning? | Preserve approximate qualifiers, measurement scope, baseline and time period when given. Do not turn average latency into P99 or a team result into a personal result. |
| Is the strongest evidence easy to find? | Put the most relevant contribution early within its entry. Keep job chronology legible rather than moving dates or mixing employers for keyword emphasis. |
| Is the summary doing different work from the detail? | Summarize a supported pattern of practice; leave its specific achievement in one primary location. Omit the summary when it only duplicates a short entry. |

### Compose sections according to the available evidence

- **Summary:** optional, usually a compact statement of actual practice and distinctive scope. No invented years, self-ratings or promise of future impact. A target role belongs in the objective when it differs from actual experience.
- **Skills:** group supplied technologies by meaningful use where possible, such as “后端开发：Node.js / NestJS（订单接口）”. Mentioned-only tools may remain tools; do not add use cases or expertise. Avoid repeating every technology in both a long summary and multiple skill paragraphs.
- **Experience:** give useful context once, then distinct contributions. Do not manufacture a separate project from each duty. A named project inside an employer can be developed when the source supports its context and contribution.
- **Projects:** prioritize distinct supplied work. Preserve its nature: course exercise, personal prototype, internal tool and production service are different settings. Do not silently promote one into another.

Choose wording and section labels for the user's language. Preserve recognizable technology names; avoid literal translation of English action-verb formulas into inflated Chinese. Do not enforce an English word-count target on Chinese summaries. Sparse material may justify a few polished bullets; rich material may justify fuller entries. Neither a fixed bullet count nor a full page is a content-quality target.

### Rich input: organize distinct evidence rather than inflate it

Fictional source: “给内部客服做过 Python 文档问答。我的部分是把文档分段、向量化、检索，再把相关内容交给模型回答。还整理了 30 个常见问题，检查回答有没有文档依据，发现问题后调整分段。没有统计准确率。”

Possible resume entry:
- “参与内部客服文档问答开发，使用 Python 实现文档分段、向量化、检索与上下文组装，为模型回答提供相关文档内容。”
- “整理 30 个常见问题，检查回答的文档依据，并根据发现的问题调整文档分段。”

The two bullets show application implementation and evaluation practice. They do not claim automated evaluation, a specific retrieval library, accuracy improvement or ownership of the whole application. A separate summary is optional, not another copy of these bullets. Here “参与” reflects the explicitly limited personal scope; do not apply it to users who explicitly owned the whole project.

## Continue safely across turns

- User acceptance such as “use this version” authorizes progressing with known facts. It does not retroactively support a skill or achievement introduced by the Agent. Correct your unsupported additions before export; explain a material correction briefly instead of silently preserving it.
- When real candidate material arrives after an explicitly requested fictional example, build the candidate profile from that material. Reusing the layout is fine; filling over a fictional profile risks leaving invented skills and achievements behind.
- On a contact-only update, change only those fields and necessary resulting layout. Do not rewrite summary/skills/projects, change template, add qualifications or re-ask the whole questionnaire. If continuing in a new session, use the prior current profile/canvas and ask only if the current revision is genuinely ambiguous.
- Supplied wording may be strengthened only by stronger supplied facts; do not weaken explicit ownership merely because the source is chat. Conflicting dates or roles require a focused clarification or omission of the disputed claim, not guessing.

Use Draft for a requested partial canvas, not simply because optional fields are missing. Master preserves this run's known facts and does not certify their external truth. Missing values remain omitted/null. See 07-artifact-contract.md for data shapes and tool states.
