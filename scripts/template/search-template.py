#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Search & Ranking Engine
Architecture: Deep Module with Pluggable Scorer Strategies (Weighted Rules + BM25 Text Search)

Design Contract:
- BaseTemplateScorer: Abstract strategy interface
- WeightedRuleScorer: Multi-criteria rule-based weighted scorer (Role 35%, Style 25%, ATS 20%, Page 10%, Density 10%)
- BM25TextScorer: Pure-Python BM25 keyword retrieval across template text documents
- HybridTemplateScorer: Weighted blend (70% Rule Score + 30% BM25 Text Score)
- search_templates(): Public facade interface
"""

import sys, os, json, argparse, math, re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists() or (curr / "src" / "templates").exists():
            return curr
        curr = curr.parent
    return Path.cwd()


@dataclass
class SearchQuery:
    role: str
    style: Optional[str] = None
    target_pages: int = 1
    density: str = "balanced"
    keywords: Optional[str] = None
    engine: str = "hybrid"  # "weighted" | "bm25" | "hybrid"


def load_templates() -> List[Dict[str, Any]]:
    root_dir = get_project_root()
    base_dir = root_dir / "src" / "templates"
    templates = []
    if not base_dir.exists():
        return templates
        
    for t_dir in sorted(base_dir.iterdir()):
        if not t_dir.is_dir() or t_dir.name == "common":
            continue
        meta_file = t_dir / "metadata.json"
        if meta_file.exists():
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                data["_directory"] = str(t_dir.relative_to(root_dir))
                templates.append(data)
            except Exception:
                pass
    return templates


# ==============================================================================
# 1. SCORER STRATEGY INTERFACE & IMPLEMENTATIONS
# ==============================================================================

class BaseTemplateScorer(ABC):
    """Abstract interface for template scoring algorithms."""
    
    @abstractmethod
    def score(self, template: Dict[str, Any], query: SearchQuery) -> float:
        """Return match score normalized between 0.0 and 100.0."""
        pass


class WeightedRuleScorer(BaseTemplateScorer):
    """
    Rule-based weighted scoring engine:
    - Role Match: 35%
    - Style Match: 25%
    - ATS Tier: 20%
    - Page Fit: 10%
    - Density Fit: 10%
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "role": 0.35,
            "style": 0.25,
            "ats": 0.20,
            "page": 0.10,
            "density": 0.10
        }

    def score(self, template: Dict[str, Any], query: SearchQuery) -> float:
        score = 0.0
        
        # 1. Role Match
        role_score = 0.0
        query_lower = query.role.lower()
        supported = [r.lower() for r in template.get("supportedRoles", [])]
        
        for r in supported:
            if r in query_lower or query_lower in r:
                role_score = 1.0
                break
                
        if role_score < 0.5:
            cat = template.get("roleCategory", "")
            if any(k in query_lower for k in ["ai", "agent", "llm", "frontend", "backend", "fullstack", "devops", "engineer"]) and "engineering" in cat:
                role_score = 0.85
            elif any(k in query_lower for k in ["manager", "product", "lead", "director", "architect", "cto"]) and "management" in cat:
                role_score = 0.85
            elif any(k in query_lower for k in ["bank", "fintech", "state", "corp", "government"]) and "corporate" in cat:
                role_score = 0.85
            else:
                role_score = 0.60
                
        score += role_score * self.weights["role"]

        # 2. Style Match
        style_score = 0.70
        if query.style:
            q_style_lower = query.style.lower()
            t_style = template.get("style", "").lower()
            t_tone = template.get("visualStyle", {}).get("tone", "").lower()
            
            if q_style_lower in t_style or q_style_lower in t_tone:
                style_score = 1.0
            elif any(k in t_style for k in q_style_lower.split("-")):
                style_score = 0.85
            else:
                style_score = 0.50
        score += style_score * self.weights["style"]

        # 3. ATS Tier
        ats_tier = template.get("atsScoreTier", "tier-1-optimal")
        ats_score = 1.0 if "optimal" in ats_tier or "tier-1" in ats_tier else 0.85
        score += ats_score * self.weights["ats"]

        # 4. Page Fit
        target_p = template.get("layout", {}).get("targetPages", 1)
        max_p = template.get("layout", {}).get("maxPages", 2)
        if query.target_pages == target_p:
            page_score = 1.0
        elif query.target_pages <= max_p:
            page_score = 0.80
        else:
            page_score = 0.50
        score += page_score * self.weights["page"]

        # 5. Density Preference
        t_density = template.get("layout", {}).get("density", "balanced")
        density_score = 1.0 if query.density == t_density else 0.80
        score += density_score * self.weights["density"]

        return round(score * 100, 1)


class BM25TextScorer(BaseTemplateScorer):
    """
    Pure Python BM25 Text Scorer across template metadata documents.
    Constructs a virtual document per template: (name, category, style, supportedRoles, tone).
    """
    
    def __init__(self, templates: Optional[List[Dict[str, Any]]] = None, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.templates = templates or load_templates()
        self.docs = [self._extract_doc(t) for t in self.templates]
        self.avg_dl = sum(len(d) for d in self.docs) / max(len(self.docs), 1)
        self.doc_freqs = self._calc_doc_freqs()

    def _extract_doc(self, template: Dict[str, Any]) -> List[str]:
        text_parts = [
            template.get("name", ""),
            template.get("style", ""),
            template.get("roleCategory", ""),
            template.get("visualStyle", {}).get("tone", ""),
            " ".join(template.get("supportedRoles", []))
        ]
        combined = " ".join(text_parts).lower()
        # Tokenize words & Chinese characters
        tokens = re.findall(r'[a-zA-Z0-9_\-]+|[\u4e00-\u9fa5]', combined)
        return tokens

    def _calc_doc_freqs(self) -> Dict[str, int]:
        freqs: Dict[str, int] = {}
        for doc in self.docs:
            for word in set(doc):
                freqs[word] = freqs.get(word, 0) + 1
        return freqs

    def score(self, template: Dict[str, Any], query: SearchQuery) -> float:
        doc = self._extract_doc(template)
        doc_len = len(doc)
        if doc_len == 0:
            return 50.0

        query_text = f"{query.role} {query.style or ''} {query.keywords or ''}".lower()
        q_tokens = re.findall(r'[a-zA-Z0-9_\-]+|[\u4e00-\u9fa5]', query_text)
        if not q_tokens:
            return 70.0

        n_docs = len(self.docs)
        score = 0.0

        for term in q_tokens:
            df = self.doc_freqs.get(term, 0)
            if df == 0:
                continue
            # Standard BM25 IDF with smoothing
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            tf = doc.count(term)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(self.avg_dl, 1)))
            score += idf * (numerator / max(denominator, 0.001))

        # Normalize score into roughly 50.0 ~ 100.0 range
        normalized = 50.0 + min(score * 15.0, 50.0)
        return round(normalized, 1)


class HybridTemplateScorer(BaseTemplateScorer):
    """
    Weighted combination of rule-based constraints and BM25 text relevance.
    Default: 70% Weighted Rules + 30% BM25 Relevance.
    """
    
    def __init__(self, rule_weight: float = 0.70, bm25_weight: float = 0.30):
        self.rule_scorer = WeightedRuleScorer()
        self.bm25_scorer = BM25TextScorer()
        self.rule_weight = rule_weight
        self.bm25_weight = bm25_weight

    def score(self, template: Dict[str, Any], query: SearchQuery) -> float:
        rule_score = self.rule_scorer.score(template, query)
        bm25_score = self.bm25_scorer.score(template, query)
        blended = (rule_score * self.rule_weight) + (bm25_score * self.bm25_weight)
        return round(blended, 1)


# ==============================================================================
# 2. PUBLIC FACADE INTERFACE (DEEP MODULE)
# ==============================================================================

def search_templates(
    role: str,
    style: Optional[str] = None,
    target_pages: int = 1,
    density: str = "balanced",
    keywords: Optional[str] = None,
    engine: str = "hybrid"
) -> List[Dict[str, Any]]:
    """
    Search and rank HTML resume templates.
    
    Args:
        role: Target job title or direction (e.g., 'AI Agent Engineer', 'Tech Lead')
        style: Preferred visual/layout style (e.g., 'single-column-minimal', 'two-column-split')
        target_pages: Expected page count (1 or 2)
        density: Information density preference ('high', 'balanced', 'spacious')
        keywords: Optional JD keywords for text matching
        engine: Scoring engine ('hybrid' | 'weighted' | 'bm25')
        
    Returns:
        List of matching templates sorted by matchScore descending.
    """
    query = SearchQuery(
        role=role,
        style=style,
        target_pages=target_pages,
        density=density,
        keywords=keywords,
        engine=engine
    )
    
    templates = load_templates()
    if not templates:
        return []

    # Select Scorer Strategy
    scorer: BaseTemplateScorer
    if engine == "bm25":
        scorer = BM25TextScorer(templates)
    elif engine == "weighted":
        scorer = WeightedRuleScorer()
    else:
        scorer = HybridTemplateScorer()

    results = []
    for t in templates:
        t_copy = dict(t)
        score_val = scorer.score(t, query)
        t_copy["matchScore"] = score_val
        t_copy["score"] = score_val
        t_copy["template"] = t
        results.append(t_copy)
        
    results.sort(key=lambda x: x.get("matchScore", 0.0), reverse=True)
    return results
def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Template Search Engine")
    parser.add_argument("role", nargs="?", default=None, help="Target role or job title (e.g. 'AI Agent Engineer')")
    parser.add_argument("--role", "-r", dest="named_role", default=None, help="Target role (named option)")
    parser.add_argument("--style", "-s", default=None, help="Style preference (minimal, modern, executive, classic)")
    parser.add_argument("--target-pages", "-p", type=int, default=1, help="Target pages (1 or 2)")
    parser.add_argument("--density", "-d", default="balanced", choices=["high", "balanced", "spacious"], help="Density")
    parser.add_argument("--keywords", "-k", default=None, help="Additional JD keywords")
    parser.add_argument("--engine", "-e", default="hybrid", choices=["hybrid", "weighted", "bm25"], help="Scoring engine")
    parser.add_argument("--json", action="store_true", help="Output raw JSON array")
    
    args = parser.parse_args()
    target_role = args.named_role or args.role
    if not target_role:
        parser.error("the following arguments are required: role (or --role / -r)")

    results = search_templates(
        role=target_role,
        style=args.style,
        target_pages=args.target_pages,
        density=args.density,
        keywords=args.keywords,
        engine=args.engine
    )
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
        
    print("=" * 80)
    print(f"  KnowMe CareerForge — Template Search Engine Results")
    print(f"  Query Role   : {target_role}")
    print(f"  Style Filter : {args.style or 'Any'}")
    print(f"  Engine       : {args.engine.upper()}")
    print(f"  Matches      : {len(results)} template(s) found")
    print("=" * 80)
    
    for idx, r in enumerate(results, 1):
        custom_tokens = r.get("customizableTokens", [])
        tokens_preview = ", ".join(custom_tokens[:4]) + ("..." if len(custom_tokens) > 4 else "")
        print(f"\n{idx}. [{r.get('matchScore')} pts] {r.get('name')} (ID: {r.get('id')})")
        print(f"   Category: {r.get('roleCategory')} | Style: {r.get('style')} | ATS Tier: {r.get('atsScoreTier')}")
        print(f"   Target Pages: {r.get('layout', {}).get('targetPages', 1)} | Density: {r.get('layout', {}).get('density')}")
        print(f"   Directory: {r.get('_directory')}")
        if tokens_preview:
            print(f"   Tokens   : {tokens_preview}")
        print("-" * 80)


if __name__ == "__main__":
    main()
