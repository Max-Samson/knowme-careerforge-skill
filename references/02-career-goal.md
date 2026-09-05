# Reference Manual 02: Career Goal Definition & Role Archetypes

> **"Know Yourself. Define Your Direction. Forge Your Opportunity."**

---

## 1. Professional Seniority Signals

Use these archetypes to guide questions, not to infer facts. Years alone do not establish seniority, ownership or proficiency. Preserve the user’s stated role and responsibility; omit unsupported claims from the following illustrative patterns.

| Seniority Tier | Core Value Proposition | Key Narrative Signals | Section Priority |
|:---|:---|:---|:---|
| **Junior (1~3 Years)** | Rapid learning, solid coding standards, reliable task delivery | Clean code, unit test coverage, framework fluency, bug resolution | Skills → Projects → Experience → Education |
| **Mid-Level (3~5 Years)** | Independent ownership, feature architecture, performance optimization | End-to-end module ownership, database tuning, API design, CI/CD | Experience → Projects → Skills → Education |
| **Senior / Lead (5~8+ Years)** | System architecture, technical leadership, cross-system trade-offs | Distributed systems, high availability, mentoring, business impact | Experience → Projects → Architecture → Skills |
| **Principal / Architect** | Technical vision, organizational strategy, governance, ROI | Architecture governance, multi-team alignment, technology selection | Experience → Leadership → Architecture → Patents |

---

## 2. Role Archetypes Knowledge Base (`src/knowledge/roles/*.json`)

Read a role profile only for a specific positioning question after candidate facts are available. `mustHaveSkills`, `niceToHaveSkills` and `evidenceSignals` describe hiring expectations and question topics; they are never defaults for personal skills, mechanisms or accomplishments. A generic role name may cover several seniority levels.

The skill ships with 9+ structured role profiles:
- `ai-agent-engineer.json`: LLM Orchestration, RAG, Tool Calling, VectorDB, Prompt Engineering
- `frontend.json`: React/Vue/Next.js, Web Vitals, Design Systems, State Management
- `java-backend.json`: Spring Boot, JVM tuning, Distributed Caching, Message Queues
- `node-fullstack.json`: TypeScript, Node.js runtime, GraphQL, Cloud Native
- `architect.json`: Distributed Systems, Domain-Driven Design, High Concurrency, Cloud Architecture
- `product-manager.json`: PRD, User Research, Data Analysis, Roadmapping, Growth

---

## 3. Core Value Proposition Formulation

If useful, write a short headline from supplied facts. The following formula is optional: omit years, strengths or impact when unknown. The example is fictional and must never fill a candidate record.
$$\text{Value Proposition} = [\text{Target Role}] + [\text{Years/Domain Focus}] + [\text{Top 2 Signature Strengths}] + [\text{Concrete Impact Deliverable}]$$

*Example*:
> **Senior AI Agent Engineer** with 5+ years building scalable LLM orchestration & enterprise RAG pipelines, delivering 40% latency reduction across multi-agent production workflows.
