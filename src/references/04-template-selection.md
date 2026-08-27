# Reference Manual 04: Template Selection & Layout Geometries

> **"Layout geometry determines information hierarchy. Select the composition that earns the candidate's strongest evidence."**

---

## 1. Core Template Matrix (Baseline 4)

| Template ID | Layout Geometry | Tone & Accent | Target Roles | Density | ATS Tier |
|:---|:---|:---|:---|:---|:---|
| `minimal` (`minimal-tech`) | Single-Column Linear Flow | Geek Minimal (Tech Blue `#2563eb`) | Backend, AI/LLM, Systems, DevOps, Fullstack | High | Tier 1 (Optimal) |
| `modern` (`modern-split-sidebar`) | Two-Column Split (32:68 Dark Sidebar) | Deep Navy (`#254665`) + Sky Blue (`#38bdf8`) | AI Agent, Frontend, Fullstack, Mobile | Balanced | Tier 1 (Optimal) |
| `executive` (`executive-split`) | Hero Banner + Two-Column (33:67 Split) | Executive Slate (`#1e293b`) + Teal (`#0f766e`) | Tech Director, Architect, PM, CTO | Balanced | Tier 1 (Optimal) |
| `classic` (`table-structured`) | 6-Column Structured Grid Table | Corporate Blue (`#1d4ed8`) + Slate | Enterprise, Fintech, Hardware, State-Owned | High | Tier 1 (Optimal) |

---

## 2. Template Search Engine (`scripts/template/search-template.py`)

Search for the optimal template via CLI:
```bash
# Hybrid Search (Default Recommended)
python3 scripts/template/search-template.py "AI Agent Engineer" --style "two-column-split" --target-pages 1

# BM25 Keyword Search
python3 scripts/template/search-template.py "Distributed Architect" --engine bm25 --json

# Weighted Multi-Criteria Rule Search
python3 scripts/template/search-template.py "Frontend Engineer" --engine weighted
```

### Search Scoring Formulation (Weighted Scorer):
$$\text{Score} = (\text{RoleMatch} \times 0.35) + (\text{StyleMatch} \times 0.25) + (\text{ATSTier} \times 0.20) + (\text{PageFit} \times 0.10) + (\text{Density} \times 0.10)$$

---

## 3. Instantiating the Intermediate HTML Canvas

```bash
python3 scripts/template/instantiate-resume.py --template modern --profile workspace/evidence-master.json --keywords "Python,LLM,RAG,FastAPI" --output workspace/resume.html
```

*The instantiator automatically inlines `src/templates/common/base.css` + `src/templates/{template}/style.css` into a single self-contained HTML file.*
