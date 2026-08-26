#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Search & Ranking Engine (BM25 + Multi-criteria scoring)
根据目标岗位、期望版式风格、目标页数与信息密度，加权检索最匹配的 HTML 简历模板。
"""

import sys, os, json, argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists() or (curr / "src" / "templates").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

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
                data["directory"] = f"src/templates/{t_dir.name}"
                templates.append(data)
            except Exception:
                pass
    return templates

def calculate_match_score(template: Dict[str, Any], query_role: str, query_style: Optional[str] = None, target_pages: int = 1, density: str = "balanced") -> float:
    score = 0.0
    
    # 1. 岗位匹配度 (Role Match - 35%)
    role_score = 0.0
    query_lower = query_role.lower()
    supported = [r.lower() for r in template.get("supportedRoles", [])]
    
    for r in supported:
        if r in query_lower or query_lower in r:
            role_score = 1.0
            break
            
    if role_score < 0.5:
        cat = template.get("roleCategory", "")
        if "ai" in query_lower or "algorithm" in query_lower or "agent" in query_lower:
            role_score = 0.95 if cat == "engineering-ai" else 0.40
        elif "product" in query_lower or "manager" in query_lower or "director" in query_lower:
            role_score = 0.95 if cat == "management-product" else 0.40
        elif "engineer" in query_lower or "architect" in query_lower:
            role_score = 0.85
        else:
            role_score = 0.60
            
    score += role_score * 0.35

    # 2. 风格匹配度 (Style Match - 25%)
    style_score = 0.70
    if query_style:
        q_style_lower = query_style.lower()
        t_style = template.get("style", "").lower()
        t_tone = template.get("visualStyle", {}).get("tone", "").lower()
        
        if q_style_lower in t_style or q_style_lower in t_tone or q_style_lower == template.get("id"):
            style_score = 1.0
        elif "minimal" in q_style_lower and "minimal" in t_style:
            style_score = 0.95
        elif "split" in q_style_lower and "split" in t_style:
            style_score = 0.95
        elif "modern" in q_style_lower and "modern" in t_tone:
            style_score = 0.95
        else:
            style_score = 0.50
    score += style_score * 0.25

    # 3. ATS 兼容评级 (ATS Tier - 20%)
    ats_tier = template.get("atsScoreTier", "tier-1-optimal")
    ats_score = 1.0 if "optimal" in ats_tier or "tier-1" in ats_tier else 0.85
    score += ats_score * 0.20

    # 4. 页数适配度 (Page Fit - 10%)
    target_p = template.get("layout", {}).get("targetPages", 1)
    max_p = template.get("layout", {}).get("maxPages", 2)
    if target_pages == target_p:
        page_score = 1.0
    elif target_pages <= max_p:
        page_score = 0.80
    else:
        page_score = 0.50
    score += page_score * 0.10

    # 5. 信息密度偏好 (Density - 10%)
    t_density = template.get("layout", {}).get("density", "balanced")
    density_score = 1.0 if density == t_density else 0.80
    score += density_score * 0.10

    return round(score * 100, 1)

def search_templates(role: str, style: Optional[str] = None, target_pages: int = 1, density: str = "balanced") -> List[Dict[str, Any]]:
    templates = load_templates()
    results = []
    
    for t in templates:
        s = calculate_match_score(t, role, style, target_pages, density)
        results.append({
            "score": s,
            "template": t
        })
        
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Template Search Engine")
    parser.add_argument("role", nargs="?", default="AI Agent Engineer", help="Target role title")
    parser.add_argument("--style", "-s", default=None, help="Desired style (minimal, modern, executive, classic)")
    parser.add_argument("--target-pages", "-p", type=int, default=1, help="Expected target pages (1 or 2)")
    parser.add_argument("--density", "-d", default="balanced", help="Information density preference (high, balanced, normal)")
    parser.add_argument("--json", action="store_true", help="Output results in raw JSON")

    args = parser.parse_args()
    results = search_templates(args.role, style=args.style, target_pages=args.target_pages, density=args.density)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("=" * 80)
    print(f"  KnowMe CareerForge — Template Recommendations for '{args.role}'")
    print("=" * 80)
    for idx, r in enumerate(results, 1):
        t = r["template"]
        print(f"{idx}. [Score: {r['score']}] {t['name']} (ID: {t['id']})")
        print(f"   Category: {t['roleCategory']} | Style: {t['style']} | ATS Tier: {t['atsScoreTier']}")
        print(f"   Target Pages: {t['layout']['targetPages']} (Max: {t['layout']['maxPages']}) | Density: {t['layout']['density']}")
        print(f"   Tone: {t['visualStyle']['tone']} | Accent: {t['visualStyle']['accentColor']}")
        print(f"   Directory: {t['directory']}")
        print("-" * 80)

if __name__ == "__main__":
    main()
