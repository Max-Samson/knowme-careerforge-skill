# Reference Manual 03: Job Description (JD) Analysis & Keyword Extraction

> **"Understand the hiring manager's unstated pain point to align your verified strengths."**

---

## 1. Automated JD Signal Parsing Protocol

Execute the JD analyzer to extract structured requirements:
```bash
python3 scripts/evidence/analyze-jd.py --jd "path/to/jd.md" --json
```

### Signal Extraction Dimensions:
1. **Target Role & Seniority Tier**: Extracted from title and years of experience requirements;
2. **Must-Have Skills (Hard Constraints)**: Top technical stacks and non-negotiable architectural competencies;
3. **Nice-to-Have Skills (Differentiators)**: Emerging tools, cloud certifications, domain bonuses;
4. **Hiring Pain Points**: High-frequency verbs indicating immediate business challenges (e.g., "reduce latency", "overhaul legacy monolithic service", "establish CI/CD").

---

## 2. Keyword Density & Highlighting Rules

Use JD terms only where the candidate has supplied matching experience. Keywords select or emphasize existing facts; they do not add skills to a Master or Variant. A technology named only by the vacancy remains a gap to discuss.

Prefer a few relevant, readable terms over repetition. There is no project-validated universal ATS keyword-density threshold. Do not claim automated screening success from keyword counts.

## 3. Writing useful bullets

Describe the supplied action and its context. Add the method and outcome only when the user provided them. FAB is an optional editing aid, not a requirement that every duty acquire an invented business impact.

For example, if the only fact is “optimized order queries”, a faithful rewrite is “Optimized order queries for the ecommerce service” only if that service context was supplied. Do not infer indexing, Redis caching, P99 latency or traffic multiples. Preserve “participated” versus “led”, and ask for consequential missing mechanisms instead of writing them as facts.
