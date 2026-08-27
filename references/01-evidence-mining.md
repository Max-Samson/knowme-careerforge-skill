# Reference Manual 01: Evidence Mining & Anti-Hallucination Gate

> **"The goal is not to make the candidate look better than they are. The goal is to make their real strengths visible to the right opportunity."**

---

## 1. L1~L3 Evidence Classification Standard

Every bullet point and technical claim on the resume MUST be grounded in traceable candidate evidence:

| Level | Evidence Source | Confidence | Usage & Phrasing Standard | Prohibited Anti-Patterns |
|:---|:---|:---|:---|:---|
| **Level 1 (Direct Strong Evidence)** | Code implementation (`src/`), config files (`package.json`, `go.mod`, `Cargo.toml`, `Dockerfile`), API contracts, CI/CD pipelines, Git commit history | 95%+ | Direct, confident assertion with quantified metrics: *"Designed dual-path retrieval pipeline using FastAPI and Qdrant, achieving 92% Top-3 recall rate."* | Fabricating business revenue or claiming ownership beyond repository boundaries. |
| **Level 2 (Structural Medium Evidence)** | Directory structure, module dependencies, database schemas, framework integrations | 80%~95% | Engineering integration verbs: *"Engineered distributed microservice endpoints for order and inventory management using gRPC."* | Exaggerating simple library imports as custom from-scratch underlying framework development. |
| **Level 3 (Contextual Weak Inference)** | Agile practices, code reviews, deployment workflows, cross-team collaboration | 60%~80% | Conservative contextual phrasing: *"Participated in system architecture reviews and collaborated with product teams on sprint delivery."* | Claiming solo leadership of large engineering teams without organizational backing. |
| **Unsupported (No Evidence)** | Facts not found in candidate records or codebases | <50% | **STRICTLY PROHIBITED FROM RESUME** | Inventing unverified degrees, false company tenures, or imaginary revenue numbers. |

---

## 2. Automated Codebase & Git Mining Protocol

Run the evidence extraction engine against local repository or workspace:
```bash
python3 scripts/evidence/extract-evidence.py --repo . --name "<Candidate Name>" --output workspace/evidence-master.json --quiet
```

### Extracted Evidence Dimensions:
1. **Git Provenance**: Author names, email, commit count, active development timeframes;
2. **Tech Stack Signatures**: Dependency parsing across 25+ language/framework ecosystems;
3. **Architecture Signals**: Monorepo setups, containerization (Docker/K8s), automated testing, CI/CD workflows;
4. **Code Volume & Distribution**: Breakdown by language and directory hierarchy.

---

## 3. Anti-Hallucination Execution Checklist

Before writing any line into `workspace/resume.html`:
- [ ] Is the primary technology verified in candidate code, config, or explicit profile?
- [ ] Is the action verb accurate to actual candidate contribution level (Led vs Implemented vs Participated)?
- [ ] Are all metrics (percentages, QPS, latency) grounded in reality rather than fabricated?
- [ ] If JD requires a skill absent from candidate evidence, mark as gap rather than hallucinating.
