#!/usr/bin/env python3
"""
KnowMe CareerForge — Resume Workspace Instantiator (Intermediate Working Canvas)
将指定模板、候选人结构化事实档案 (evidence-master.json) 与 JD 关键词高亮组装为自包含的单文件 HTML 工作区修改场。
"""

import sys, os, json, argparse, re
from pathlib import Path
from typing import Dict, Any, Optional, List

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists() or (curr / "src" / "templates").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def highlight_keywords(text: str, keywords: List[str]) -> str:
    if not keywords or not text:
        return text
    for kw in keywords:
        kw_clean = kw.strip()
        if kw_clean:
            pattern = re.compile(rf'(?<!<strong>)(?<![<\w/])({re.escape(kw_clean)})(?![>\w])(?!</strong>)', re.IGNORECASE)
            text = pattern.sub(r"<strong>\1</strong>", text)
    return text

def render_profile_into_html(html_str: str, profile: Dict[str, Any], keywords: Optional[List[str]] = None) -> str:
    basics = profile.get("basics", {})
    name = basics.get("name", "")
    title = basics.get("title", "")
    phone = basics.get("phone", "")
    email = basics.get("email", "")
    location = basics.get("location", "")
    github = basics.get("github", "")

    # 1. 替换基础信息
    if name:
        html_str = re.sub(r'(<h1[^>]*class="[^"]*candidate-name[^"]*"[^>]*>).*?(</h1>)', rf'\g<1>{name}\g<2>', html_str)
        html_str = re.sub(r'(<title>).*?(</title>)', f'<title>{name} - 个人简历</title>', html_str)
    
    if title:
        html_str = re.sub(r'(<(?:p|span)[^>]*class="[^"]*(?:job-target|target-title)[^"]*"[^>]*>).*?(</(?:p|span)>)', rf'\g<1>求职意向：{title}\g<2>', html_str)

    if phone:
        html_str = re.sub(r'138-0000-0000|\b1[3-9]\d{9}\b|\+?\d{1,4}[-\s]?\d{7,11}', phone, html_str)
    
    if email:
        html_str = re.sub(r'[a-zA-Z0-9_.+-]+@example\.com|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', email, html_str)

    if location:
        html_str = re.sub(r'北京\s*[·•-]\s*海淀(?:区)?', location, html_str)

    if github:
        html_str = re.sub(r'github\.com/[a-zA-Z0-9_-]+', github.replace("https://", "").replace("http://", ""), html_str)

    # 2. 注入经历
    experiences = profile.get("experience", [])
    if experiences and '<section class="resume-section" id="experience">' in html_str:
        exp_html_items = []
        for exp in experiences:
            bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in exp.get("bullets", [])])
            exp_html_items.append(f"""
        <div class="experience-item">
          <div class="item-header">
            <div class="item-title-group">
              <span class="org-name">{exp.get('company', '')}</span>
              <span class="role-badge">{exp.get('role', '')}</span>
            </div>
            <span class="date-range">{exp.get('startDate', '')} - {exp.get('endDate', '')}</span>
          </div>
          <ul class="bullet-list">
            {bullets_html}
          </ul>
        </div>""")
        
        exp_block_pattern = re.compile(r'(<section[^>]*id="experience"[^>]*>.*?<h2[^>]*>.*?</h2>\s*).*?(</section>)', re.DOTALL)
        if exp_block_pattern.search(html_str):
            html_str = exp_block_pattern.sub(rf'\g<1>{"".join(exp_html_items)}\n      \g<2>', html_str)

    # 3. 注入项目
    projects = profile.get("projects", [])
    if projects and '<section class="resume-section" id="projects">' in html_str:
        proj_html_items = []
        for proj in projects:
            bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in proj.get("bullets", [])])
            tech_tags_html = "".join([f'<span class="tech-tag">{t}</span>' for t in proj.get("techStack", [])])
            proj_html_items.append(f"""
        <div class="project-item">
          <div class="item-header">
            <div class="item-title-group">
              <span class="project-name">{proj.get('name', '')}</span>
              <span class="role-badge">{proj.get('role', '')}</span>
            </div>
            <span class="date-range">{proj.get('startDate', '')} - {proj.get('endDate', '')}</span>
          </div>
          <div class="tech-stack-tags">
            {tech_tags_html}
          </div>
          <ul class="bullet-list">
            {bullets_html}
          </ul>
        </div>""")
        
        proj_block_pattern = re.compile(r'(<section[^>]*id="projects"[^>]*>.*?<h2[^>]*>.*?</h2>\s*).*?(</section>)', re.DOTALL)
        if proj_block_pattern.search(html_str):
            html_str = proj_block_pattern.sub(rf'\g<1>{"".join(proj_html_items)}\n      \g<2>', html_str)

    return html_str

def instantiate_workspace(template_id: str, profile_path: Optional[str] = None, keywords: Optional[str] = None, output_path: str = "workspace/resume.html") -> Path:
    base_dir = get_project_root()
    template_dir = base_dir / "src" / "templates" / template_id
    
    if not template_dir.exists():
        for sub in (base_dir / "src" / "templates").iterdir():
            if sub.is_dir() and (sub / "metadata.json").exists():
                try:
                    meta = json.loads((sub / "metadata.json").read_text(encoding="utf-8"))
                    if meta.get("id") == template_id:
                        template_dir = sub
                        break
                except Exception:
                    pass

    if not template_dir.exists():
        raise ValueError(f"Template '{template_id}' not found in src/templates/")
        
    html_file = template_dir / "template.html"
    css_file = template_dir / "style.css"
    
    if not html_file.exists() or not css_file.exists():
        raise FileNotFoundError(f"template.html or style.css missing in {template_dir}")
        
    html_content = html_file.read_text(encoding="utf-8")
    css_content = css_file.read_text(encoding="utf-8")
    
    inlined_html = html_content.replace(
        '<link rel="stylesheet" href="style.css">',
        f'<style>\n{css_content}\n  </style>'
    )
    
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []

    if profile_path and Path(profile_path).exists():
        try:
            profile_data = json.loads(Path(profile_path).read_text(encoding="utf-8"))
            inlined_html = render_profile_into_html(inlined_html, profile_data, kw_list)
        except Exception as e:
            print(f"[!] Warning: Failed to inject profile data: {e}")
    elif kw_list:
        inlined_html = highlight_keywords(inlined_html, kw_list)
        
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(inlined_html, encoding="utf-8")
    
    print("==============================================================")
    print(f"  KnowMe CareerForge — Intermediate Canvas Instantiated!")
    print(f"  Selected Template : {template_id} ({template_dir.name})")
    print(f"  Profile Injected  : {profile_path or 'Default Template Content'}")
    print(f"  Working Canvas    : {out_file.resolve()}")
    print("==============================================================")
    return out_file

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Workspace Instantiator")
    parser.add_argument("--template", "-t", required=True, help="Template ID (minimal, modern, executive, classic)")
    parser.add_argument("--profile", "-p", default=None, help="Path to evidence-master.json candidate profile")
    parser.add_argument("--keywords", "-k", default=None, help="Comma-separated keywords to highlight (e.g. 'Python,LLM,RAG')")
    parser.add_argument("--output", "-o", default="workspace/resume.html", help="Output canvas path (default: workspace/resume.html)")

    args = parser.parse_args()
    instantiate_workspace(args.template, profile_path=args.profile, keywords=args.keywords, output_path=args.output)

if __name__ == "__main__":
    main()
