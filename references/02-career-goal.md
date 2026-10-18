# Reference Manual 02: Career Goal Definition & Role Archetypes

> **"Know Yourself. Define Your Direction. Forge Your Opportunity."**

---

## 1. Position from demonstrated scope

Use the user's actual responsibility and target to choose emphasis. Years and titles provide context, not proof of seniority. The same candidate may have strong implementation evidence but limited leadership evidence; express each at its supported level.

| Supplied evidence | Useful emphasis | Possible leading section |
| --- | --- | --- |
| Course, personal or internship projects | Concrete implementation and problem solving; preserve the project setting | Relevant projects or education |
| Delivered modules or features | Personal contribution, methods and actual delivery scope | Work experience |
| System decisions and cross-service trade-offs | What was decided, why, and the user's actual authority | Relevant work or projects |
| Team coordination or organizational responsibility | Actual coordination scope, decisions and observed outcomes | Work experience |

These are editorial options, not an automatic section order or a requirement to create “Architecture”, “Leadership” or “Patents” sections. Use the strongest supplied evidence first within a clear career narrative.

## 2. Role Archetypes Knowledge Base (`src/knowledge/roles/*.json`)

Read the relevant role profile when positioning or ability expansion would improve supplied candidate material. Treat its section order as a suggestion; demonstrated strengths and the target audience determine the actual hierarchy. `mustHaveSkills`, `niceToHaveSkills` and `evidenceSignals` describe hiring expectations and question topics; they are never defaults for personal skills, mechanisms or accomplishments. A generic role name may cover several seniority levels.

The skill ships with 9+ structured role profiles:
- `ai-agent-engineer.json`: LLM Orchestration, RAG, Tool Calling, VectorDB, Prompt Engineering
- `frontend.json`: React/Vue/Next.js, Web Vitals, Design Systems, State Management
- `java-backend.json`: Spring Boot, JVM tuning, Distributed Caching, Message Queues
- `node-fullstack.json`: TypeScript, Node.js runtime, GraphQL, Cloud Native
- `architect.json`: Distributed Systems, Domain-Driven Design, High Concurrency, Cloud Architecture
- `product-manager.json`: PRD, User Research, Data Analysis, Roadmapping, Growth

---

## 3. Write a useful summary when the evidence warrants one

Select a supported pattern of work plus a distinctive context or responsibility. Mention a result only when it adds information beyond the detailed entry. A short profile does not need a summary. Do not fill a formula with years, strengths and impact that the source does not provide.

Fictional source: “用 Python 做过内部文档问答，自己做了文档检索与模型回答衔接，也整理常见问题检查回答依据。”

Possible summary: “具有 Python 文档问答应用开发经验，实践覆盖检索与模型回答衔接、基于常见问题的回答检查。”

Detailed bullets should then supply the concrete implementation and checking work. This source does not justify “资深 Agent 架构师”, “端到端多智能体平台” or a quantified improvement. For a single short project, prefer its concrete bullets and omit this summary.

## 4. Use role templates as reasoning aids

Choose one relevant role, then connect each promising `evidenceSignals` topic to an actual user action. Classify it as direct support, transferable support, or unknown. Develop only supported topics into resume prose. `mustHaveSkills` describes the archetype, not a universal hiring requirement or a personal qualification; a supplied JD and the candidate's facts take precedence.

For AI Agent engineering, consider the following angles only when the user describes related work:

| Supplied work | Ability that may be expressed | Detail worth asking about |
| --- | --- | --- |
| Implemented workflow nodes and branches | Workflow orchestration implementation | Actual state transitions and personal scope |
| Connected a model to external tools | Tool integration | Tool purpose, argument handling, failure behavior actually implemented |
| Retrieved documents for model answers | RAG application development | Retrieval steps, corpus, evaluation if performed |
| Compared answers against a test set | Model/application evaluation practice | Evaluation criteria and observed findings |
| Deployed and maintained an application | Application delivery and maintenance | Actual users, operational responsibility, observed issues |

These angles do not require all candidates to have all five capabilities. A simple LLM API application need not be promoted into a multi-agent system. Use the same method for frontend, backend, product and other roles: domain knowledge helps interpret actual work, not manufacture experience.

For a transition, show the original stack honestly and foreground reusable problem-solving evidence. A role objective may name the destination; actual job titles and historical projects retain their identities. For experienced candidates with strong work evidence, place that evidence before a long skills catalog; for students, relevant projects or education may lead.
