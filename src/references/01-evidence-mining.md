# Turn supplied facts into resume claims

Read this when composing or materially rewriting candidate content. Compare with the user's original messages or supplied resume, not just an Agent-generated profile. Tools verify that profile text survives rendering; they cannot establish that the profile was faithful in the first place.

## Compose, then check against the source

1. Identify supplied facts and the target role separately. Treat role/JD knowledge as requirements to compare, not personal qualifications. Do not read role profiles for a straightforward rewrite; consult them only for a specific positioning question.
2. Write a concise draft of the content. Every skill, responsibility, mechanism, result and level of proficiency must be supported by supplied material. Professional editing can improve order and clarity without increasing ownership, scope or certainty.
3. Before saving the profile, compare the claims with the original source. Remove unsupported additions; ask only when a consequential ambiguity prevents a useful result. Keep this comparison internal, without a separate report or approval round. If helpful for a nontrivial rewrite, the existing bullet `evidenceSource` string can record a short source quotation; it is not printed and is not an independent verification claim.

Check each changed dimension: **technology · ownership · scope · mechanism · result · certainty**. A target title can go in the job objective; it cannot change an actual employment title, create years of experience in another stack, or become an item in skills.

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

## Continue safely across turns

- User acceptance such as “use this version” authorizes progressing with known facts. It does not retroactively support a skill or achievement introduced by the Agent. Correct your unsupported additions before export; explain a material correction briefly instead of silently preserving it.
- When real candidate material arrives after an explicitly requested fictional example, build the candidate profile from that material. Reusing the layout is fine; filling over a fictional profile risks leaving invented skills and achievements behind.
- On a contact-only update, change only those fields and necessary resulting layout. Do not rewrite summary/skills/projects, change template, add qualifications or re-ask the whole questionnaire. If continuing in a new session, use the prior current profile/canvas and ask only if the current revision is genuinely ambiguous.
- Supplied wording may be strengthened only by stronger supplied facts; do not weaken explicit ownership merely because the source is chat. Conflicting dates or roles require a focused clarification or omission of the disputed claim, not guessing.

Use Draft for a requested partial canvas, not simply because optional fields are missing. Master preserves this run's known facts and does not certify their external truth. Missing values remain omitted/null. See 07-artifact-contract.md for data shapes and tool states.
