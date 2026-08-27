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

In `workspace/resume.html`, inject JD keywords to pass ATS automated screening while remaining natural for human reviewers:

- **Primary Stack (Top 3~5 Keywords)**: Wrap with `<strong>` tags inside bullet points where evidence exists;
- **Technology Badges**: Place in `.tech-tags` or `.tech-badge` spans;
- **Density Control**: Maintain keyword density around 2.5%~4.0% of total words to prevent ATS keyword stuffing penalties.

---

## 3. FAB (Feature-Advantage-Benefit) Bullet Engineering

Structure every project bullet point using the FAB formula:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Feature (技术动作)│ ────> │ Advantage (技术优势)│ ────> │  Benefit (业务价值) │
│ Exact tech & tool │       │ Architectural gain│     │ Quantified impact│
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

*Before (Weak)*: Worked on database and improved query performance.  
*After (FAB Standard)*: Refactored PostgreSQL indexing and introduced Redis multi-tier caching (**Feature**), cutting P99 query latency from 850ms to 45ms (**Advantage**), supporting 10x traffic spike during peak sales (**Benefit**).
