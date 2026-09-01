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
    """
    Intelligently inject candidate profile facts into any of the 4 template geometries:
    - minimal (single-column tech)
    - modern (two-column split sidebar)
    - executive (hero banner + two-column)
    - classic (structured table grid)
    """
    basics = profile.get("basics", {})
    name = basics.get("name", "")
    title = basics.get("title", "")
    phone = basics.get("phone", "")
    email = basics.get("email", "")
    location = basics.get("location", "")
    github = basics.get("github", "")
    summary = basics.get("summary", "")

    # === 1. 基础信息注入 (BASICS) ===
    if name:
        html_str = re.sub(r'(<h1[^>]*class="[^"]*candidate-name[^"]*"[^>]*>).*?(</h1>)', rf'\g<1>{name}\g<2>', html_str)
        html_str = re.sub(r'(<td[^>]*class="[^"]*candidate-name[^"]*"[^>]*>).*?(</td>)', rf'\g<1>{name}\g<2>', html_str)
        html_str = re.sub(r'(<title>).*?(</title>)', f'<title>{name} - 个人简历</title>', html_str)
    
    if title:
        # Match job-target or target-title or candidate-title
        def _sub_title(m):
            tag_open = m.group(1)
            tag_close = m.group(2)
            if "job-target" in tag_open or "target-title" in tag_open:
                # keep prefix if existed
                if "求职意向" in m.group(0):
                    return f"{tag_open}求职意向：{title}{tag_close}"
                return f"{tag_open}{title}{tag_close}"
            elif "candidate-title" in tag_open:
                return f"{tag_open}{title}{tag_close}"
            return f"{tag_open}{title}{tag_close}"

        html_str = re.sub(r'(<(?:p|span|strong)[^>]*class="[^"]*(?:job-target|target-title|candidate-title)[^"]*"[^>]*>).*?(</(?:p|span|strong)>)', _sub_title, html_str)

    if summary:
        html_str = re.sub(r'(<p[^>]*class="[^"]*value-prop[^"]*"[^>]*>).*?(</p>)', rf'\g<1>{summary}\g<2>', html_str)

    if phone:
        html_str = re.sub(r'138-0000-0000|\b1[3-9]\d{9}\b|\+?\d{1,4}[-\s]?\d{7,11}', phone, html_str)
    
    if email:
        html_str = re.sub(r'[a-zA-Z0-9_.+-]+@example\.com|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', email, html_str)

    if location:
        html_str = re.sub(r'北京\s*[·•/\\-]\s*海淀(?:区)?|北京\s*/\s*远程', location, html_str)

    if github:
        clean_gh = github.replace("https://", "").replace("http://", "")
        html_str = re.sub(r'github\.com/[a-zA-Z0-9_-]+', clean_gh, html_str)

    # === 2. 专业技能注入 (SKILLS) ===
    skills = profile.get("skills", [])
    if skills:
        # 2.1 Minimal 模板技能区
        if '<div class="skills-content">' in html_str:
            skill_rows = []
            for s in skills:
                cat = s.get("category", "")
                items_str = "、".join(s.get("items", []))
                skill_rows.append(f"""
        <div class="skill-row">
          <span class="skill-category">{cat}：</span>
          <span class="skill-items">{highlight_keywords(items_str, keywords or [])}</span>
        </div>""")
            skills_pattern = re.compile(r'(<div class="skills-content">).*?(</div>\s*</section>)', re.DOTALL)
            if skills_pattern.search(html_str):
                html_str = skills_pattern.sub(rf'\g<1>{"".join(skill_rows)}\n      \g<2>', html_str)

        # 2.2 Executive 模板技能标签云 (tag-cloud)
        if '<div class="tag-cloud">' in html_str:
            tag_items = []
            all_items = []
            for s in skills:
                all_items.extend(s.get("highlighted", []) or s.get("items", [])[:3])
            for item in all_items[:10]:
                tag_items.append(f'<span class="tag">{item}</span>')
            tag_cloud_pattern = re.compile(r'(<div class="tag-cloud">).*?(</div>)', re.DOTALL)
            if tag_cloud_pattern.search(html_str):
                html_str = tag_cloud_pattern.sub(rf'\g<1>\n            {"".join(tag_items)}\n          \g<2>', html_str)

        # 2.3 Classic 模板表格技能行
        if 'id="skills"' in html_str and '<table class="resume-grid-table">' in html_str:
            skill_tr_items = []
            for s in skills[:3]:
                cat = s.get("category", "")
                items_str = "、".join(s.get("items", []))
                skill_tr_items.append(f"""
      <tr>
        <td class="cell-label">{cat}</td>
        <td colspan="5" class="cell-content">
          {highlight_keywords(items_str, keywords or [])}
        </td>
      </tr>""")
            skills_table_pattern = re.compile(r'(<tr>\s*<td colspan="6" class="section-header-cell" id="skills">.*?</tr>).*?(<tr>\s*<td colspan="6" class="section-header-cell" id="experience">)', re.DOTALL)
            if skills_table_pattern.search(html_str):
                html_str = skills_table_pattern.sub(rf'\g<1>{"".join(skill_tr_items)}\n\n      \g<2>', html_str)

    # === 3. 工作经历注入 (EXPERIENCE) ===
    experiences = profile.get("experience", [])
    if experiences:
        # 3.1 Standard section-based (minimal, modern)
        if '<section class="resume-section" id="experience">' in html_str:
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

        # 3.2 Executive 模板 (milestone-item in right-col)
        if '<div class="milestone-item">' in html_str:
            mile_items = []
            for exp in experiences:
                bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in exp.get("bullets", [])])
                mile_items.append(f"""
          <div class="milestone-item">
            <div class="item-header">
              <div class="header-left">
                <span class="org-name">{exp.get('company', '')}</span>
                <span class="role-name">{exp.get('role', '')}</span>
              </div>
              <span class="date-range">{exp.get('startDate', '')} - {exp.get('endDate', '')}</span>
            </div>
            <ul class="bullet-list">
              {bullets_html}
            </ul>
          </div>""")
            for proj in profile.get("projects", []):
                bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in proj.get("bullets", [])])
                mile_items.append(f"""
          <div class="milestone-item">
            <div class="item-header">
              <div class="header-left">
                <span class="org-name">{proj.get('name', '')}</span>
                <span class="role-name">{proj.get('role', '')}</span>
              </div>
              <span class="date-range">{proj.get('startDate', '')} - {proj.get('endDate', '')}</span>
            </div>
            <ul class="bullet-list">
              {bullets_html}
            </ul>
          </div>""")
            mile_pattern = re.compile(r'(<main class="right-col">\s*<section class="sub-section">\s*<h2 class="main-title">.*?</h2>).*?(</section>\s*</main>)', re.DOTALL)
            if mile_pattern.search(html_str):
                html_str = mile_pattern.sub(rf'\g<1>{"".join(mile_items)}\n        \g<2>', html_str)
        # 3.3 Classic 模板 (table tr rows in #experience)
        if 'id="experience"' in html_str and '<table class="resume-grid-table">' in html_str:
            exp_table_rows = []
            for exp in experiences:
                bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in exp.get("bullets", [])])
                exp_table_rows.append(f"""
      <tr>
        <td class="cell-label date-col">{exp.get('startDate', '')} - {exp.get('endDate', '')}</td>
        <td colspan="5" class="cell-content">
          <div class="exp-header">
            <strong>{exp.get('company', '')}</strong> · {exp.get('role', '')}
          </div>
          <ul class="exp-bullets">
            {bullets_html}
          </ul>
        </td>
      </tr>""")
            exp_table_pattern = re.compile(r'(<tr>\s*<td colspan="6" class="section-header-cell" id="experience">.*?</tr>).*?(<tr>\s*<td colspan="6" class="section-header-cell" id="projects">)', re.DOTALL)
            if exp_table_pattern.search(html_str):
                html_str = exp_table_pattern.sub(rf'\g<1>{"".join(exp_table_rows)}\n\n      \g<2>', html_str)

    # === 4. 核心项目注入 (PROJECTS) ===
    projects = profile.get("projects", [])
    if projects:
        # 4.1 Standard section-based (minimal, modern)
        if '<section class="resume-section" id="projects">' in html_str:
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

        # 4.2 Classic 模板项目行
        if 'id="projects"' in html_str and '<table class="resume-grid-table">' in html_str:
            proj_table_rows = []
            for proj in projects:
                bullets_html = "".join([f"<li>{highlight_keywords(b.get('text', ''), keywords or [])}</li>" for b in proj.get("bullets", [])])
                proj_table_rows.append(f"""
      <tr>
        <td class="cell-label date-col">{proj.get('startDate', '')} - {proj.get('endDate', '')}</td>
        <td colspan="5" class="cell-content">
          <div class="exp-header">
            <strong>{proj.get('name', '')}</strong> ({proj.get('role', '')})
          </div>
          <ul class="exp-bullets">
            {bullets_html}
          </ul>
        </td>
      </tr>""")
            proj_table_pattern = re.compile(r'(<tr>\s*<td colspan="6" class="section-header-cell" id="projects">.*?</tr>).*?(<tr>\s*<td colspan="6" class="section-header-cell" id="education">)', re.DOTALL)
            if proj_table_pattern.search(html_str):
                html_str = proj_table_pattern.sub(rf'\g<1>{"".join(proj_table_rows)}\n\n      \g<2>', html_str)

    # === 5. 教育背景注入 (EDUCATION) ===
    education = profile.get("education", [])
    if education:
        edu_first = education[0]
        inst = edu_first.get("institution", "")
        deg = edu_first.get("degree", "")
        start_d = edu_first.get("startDate", "")
        end_d = edu_first.get("endDate", "")
        edu_summary = edu_first.get("summary", "")
        gpa = edu_first.get("gpa", "")

        edu_desc_text = f"GPA: {gpa}" if gpa else ""
        if edu_summary:
            edu_desc_text = f"{edu_desc_text} · {edu_summary}" if edu_desc_text else edu_summary
        if not edu_desc_text:
            edu_desc_text = "统招全日制 · 优秀毕业生"

        # 5.1 Minimal 模板教育区
        if '<section class="resume-section" id="education">' in html_str and 'class="education-item"' in html_str:
            edu_minimal_html = f"""
      <div class="education-item">
        <div class="item-header">
          <div class="item-title-group">
            <span class="org-name">{inst}</span>
            <span class="role-badge">{deg}</span>
          </div>
          <span class="date-range">{start_d} - {end_d}</span>
        </div>
        <p class="edu-detail">{edu_desc_text}</p>
      </div>"""
            edu_min_pattern = re.compile(r'(<section[^>]*id="education"[^>]*>.*?<h2[^>]*>.*?</h2>\s*).*?(</section>)', re.DOTALL)
            if edu_min_pattern.search(html_str):
                html_str = edu_min_pattern.sub(rf'\g<1>{edu_minimal_html}\n    \g<2>', html_str)

        # 5.2 Modern 模板教育区
        elif '<section class="resume-section" id="education">' in html_str:
            edu_modern_html = f"""
        <div class="timeline-item">
          <div class="item-header">
            <div class="item-title-group">
              <span class="org-name">{inst}</span>
              <span class="role-title">{deg}</span>
            </div>
            <span class="date-range">{start_d} - {end_d}</span>
          </div>
          <p class="edu-desc">{edu_desc_text}</p>
        </div>"""
            edu_mod_pattern = re.compile(r'(<section[^>]*id="education"[^>]*>.*?<h2[^>]*>.*?</h2>\s*).*?(</section>)', re.DOTALL)
            if edu_mod_pattern.search(html_str):
                html_str = edu_mod_pattern.sub(rf'\g<1>{edu_modern_html}\n      \g<2>', html_str)

        # 5.3 Executive 模板教育块
        if '<div class="edu-block">' in html_str:
            edu_exec_html = f"""<div class="edu-block">
            <div class="edu-school">{inst}</div>
            <div class="edu-major">{deg}</div>
            <div class="edu-date">{start_d} - {end_d}</div>
          </div>"""
            edu_exec_pattern = re.compile(r'<div class="edu-block">.*?</div>\s*</div>', re.DOTALL)
            if edu_exec_pattern.search(html_str):
                html_str = edu_exec_pattern.sub(edu_exec_html, html_str)
            else:
                html_str = re.sub(r'<div class="edu-block">.*?</div>', edu_exec_html, html_str, flags=re.DOTALL)

        # 5.4 Classic 模板表格教育行
        if 'id="education"' in html_str and '<table class="resume-grid-table">' in html_str:
            edu_classic_html = f"""
      <tr>
        <td class="cell-label date-col">{start_d} - {end_d}</td>
        <td colspan="5" class="cell-content">
          <strong>{inst}</strong> · {deg} · {edu_desc_text}
        </td>
      </tr>"""
            edu_cls_pattern = re.compile(r'(<tr>\s*<td colspan="6" class="section-header-cell" id="education">.*?</tr>).*?(</table>)', re.DOTALL)
            if edu_cls_pattern.search(html_str):
                html_str = edu_cls_pattern.sub(rf'\g<1>{edu_classic_html}\n    \g<2>', html_str)

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
    base_css_file = base_dir / "src" / "templates" / "common" / "base.css"
    
    if not html_file.exists() or not css_file.exists():
        raise FileNotFoundError(f"template.html or style.css missing in {template_dir}")
        
    html_content = html_file.read_text(encoding="utf-8")
    css_content = css_file.read_text(encoding="utf-8")
    
    combined_css = ""
    if base_css_file.exists():
        combined_css = base_css_file.read_text(encoding="utf-8") + "\n\n/* === TEMPLATE SPECIFIC STYLES === */\n" + css_content
    else:
        combined_css = css_content
    
    inlined_html = html_content.replace(
        '<link rel="stylesheet" href="style.css">',
        f'<style>\n{combined_css}\n  </style>'
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
