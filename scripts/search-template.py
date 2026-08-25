#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Search & Ranking Engine (BM25 + Multi-criteria scoring)
根据目标岗位、期望版式风格、目标页数与信息密度，加权检索最匹配的 HTML 简历模板。
"""

import sys, os, json, argparse
from pathlib import Path

def load_templates():
    base_dir = Path(__file__).resolve().parent.parent / "src" / "templates"
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
            except Exception as e:
                pass
    return templates

def calculate_match_score(template, query_role, query_style=None, target_pages=1, density="balanced"):
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
        if "tech" in query_lower or "engineer" in query_lower or "ai" in query_lower or "研发" in query_lower:
            role_score = 0.90 if cat == "engineering-ai" else 0.40
        elif "manage" in query_lower or "lead" in query_lower or "director" in query_lower or "总监" in query_lower or "架构" in query_lower or "产品" in query_lower:
            role_score = 0.90 if cat == "management-product" else 0.50
        else:
            role_score = 0.60
            
    score += role_score * 0.35

    # 2. 风格匹配度 (Style Match - 25%)
    style_score = 0.70
    if query_style:
        q_style_lower = query_style.lower()
        t_style = template.get("style", "").lower()
        t_id = template.get("id", "").lower()
        if q_style_lower in t_style or q_style_lower in t_id:
            style_score = 1.0
        elif "single" in q_style_lower and "single" in t_style:
            style_score = 1.0
        elif "split" in q_style_lower or "double" in q_style_lower or "column" in q_style_lower:
            style_score = 1.0 if "two-column" in t_style else 0.50
        elif "table" in q_style_lower or "grid" in q_style_lower:
            style_score = 1.0 if "table" in t_style else 0.40
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

def search_templates(role, style=None, target_pages=1, density="balanced"):
    templates = load_templates()
    if not templates:
        return []
    
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
    parser.add_argument("role", nargs="?", default="AI Agent Engineer", help="Target role title (e.g. 'AI Agent Engineer', 'Frontend')")
    parser.add_argument("--style", default=None, help="Style filter: minimal, modern, executive, classic, single-column, two-column, table")
    parser.add_argument("--target-pages", type=int, default=1, help="Expected page count (1 or 2)")
    parser.add_argument("--density", default="balanced", choices=["high", "balanced", "relaxed"], help="Information density")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    results = search_templates(args.role, args.style, args.target_pages, args.density)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("=" * 80)
    print(f"  KnowMe CareerForge — Template Search Results")
    print(f"  Target Role : {args.role}")
    print(f"  Style Pref  : {args.style or 'Any'}")
    print(f"  Target Pages: {args.target_pages} | Density: {args.density}")
    print("=" * 80)

    if not results:
        print("No matching templates found.")
        return

    for idx, r in enumerate(results, 1):
        t = r["template"]
        print(f"{idx}. [Score: {r['score']}] {t.get('name')} (ID: {t.get('id')})")
        print(f"   Category: {t.get('roleCategory')} | Style: {t.get('style')} | ATS Tier: {t.get('atsScoreTier')}")
        print(f"   Target Pages: {t.get('layout', {}).get('targetPages')} (Max: {t.get('layout', {}).get('maxPages')}) | Density: {t.get('layout', {}).get('density')}")
        print(f"   Customizable Tokens: {', '.join(t.get('customizableTokens', [])[:4])}")
        print(f"   Directory: {t.get('directory')}")
        print("-" * 80)

if __name__ == "__main__":
    main()
