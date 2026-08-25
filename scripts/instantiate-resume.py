#!/usr/bin/env python3
"""
KnowMe CareerForge — Resume Workspace Instantiator
将指定模板与关键词高亮组装为自包含的单文件 HTML 工作区修改场 (Intermediate Working Canvas)。
"""

import sys, os, json, argparse, re
from pathlib import Path

def highlight_keywords(text, keywords):
    if not keywords:
        return text
    for kw in keywords:
        kw_clean = kw.strip()
        if kw_clean:
            # 避免对已有标签属性进行错误替换
            pattern = re.compile(rf'(?<![<\w/])({re.escape(kw_clean)})(?![>\w])', re.IGNORECASE)
            text = pattern.sub(lambda m: f"<strong>{m.group(0)}</strong>", text)
    return text

def instantiate_workspace(template_id, keywords=None, output_path="workspace/resume.html"):
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    
    template_dir = base_dir / "src" / "templates" / template_id
    
    if not template_dir.exists():
        # 尝试通过 ID 查找
        for sub in (base_dir / "src" / "templates").iterdir():
            if sub.is_dir() and (sub / "metadata.json").exists():
                try:
                    meta = json.loads((sub / "metadata.json").read_text(encoding="utf-8"))
                    if meta.get("id") == template_id:
                        template_dir = sub
                        break
                except:
                    pass

    if not template_dir.exists():
        raise ValueError(f"Template '{template_id}' not found in src/templates/")
        
    html_file = template_dir / "template.html"
    css_file = template_dir / "style.css"
    
    if not html_file.exists() or not css_file.exists():
        raise FileNotFoundError(f"template.html or style.css missing in {template_dir}")
        
    html_content = html_file.read_text(encoding="utf-8")
    css_content = css_file.read_text(encoding="utf-8")
    
    # 将外部 style.css 内联进 HTML，形成零依赖单文件工作场
    inlined_html = html_content.replace(
        '<link rel="stylesheet" href="style.css">',
        f'<style>\n{css_content}\n  </style>'
    )
    
    # 注入关键词高亮
    if keywords:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        inlined_html = highlight_keywords(inlined_html, kw_list)
        
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(inlined_html, encoding="utf-8")
    
    print("=" * 70)
    print(f"  KnowMe CareerForge — Intermediate Canvas Instantiated!")
    print(f"  Selected Template : {template_id} ({template_dir.name})")
    print(f"  Working Canvas    : {out_file.resolve()}")
    print("=" * 70)
    return out_file

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Workspace Instantiator")
    parser.add_argument("--template", "-t", required=True, help="Template ID (minimal, modern, executive, classic)")
    parser.add_argument("--keywords", "-k", default=None, help="Comma-separated keywords to highlight (e.g. 'Python,LLM,RAG')")
    parser.add_argument("--output", "-o", default="workspace/resume.html", help="Output canvas path (default: workspace/resume.html)")

    args = parser.parse_args()
    instantiate_workspace(args.template, keywords=args.keywords, output_path=args.output)

if __name__ == "__main__":
    main()
