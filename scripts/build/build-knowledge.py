#!/usr/bin/env python3
"""
KnowMe CareerForge — Knowledge & Template Index Compiler
扫描 src/knowledge/ 与 src/templates/，生成全量注册表与知识库索引。
"""

import sys, os, json, re
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def build_knowledge_index():
    base_dir = get_project_root()
    knowledge_dir = base_dir / "src" / "knowledge"
    templates_dir = base_dir / "src" / "templates"
    
    # 1. 扫描岗位画像
    roles_dir = knowledge_dir / "roles"
    roles = []
    if roles_dir.exists():
        for f in sorted(roles_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                roles.append(data)
            except Exception as e:
                print(f"[!] Error parsing role {f.name}: {e}")
                
    # 2. 扫描模板
    templates = []
    if templates_dir.exists():
        for t_dir in sorted(templates_dir.iterdir()):
            if not t_dir.is_dir() or t_dir.name == "common":
                continue
            meta_file = t_dir / "metadata.json"
            if meta_file.exists():
                try:
                    data = json.loads(meta_file.read_text(encoding="utf-8"))
                    data["directory"] = f"src/templates/{t_dir.name}"
                    
                    # 侦测 CSS 变量
                    css_file = t_dir / "style.css"
                    if css_file.exists():
                        css_text = css_file.read_text(encoding="utf-8")
                        vars_found = sorted(list(set(re.findall(r'--resume-[\w-]+', css_text))))
                        data["detectedTokens"] = vars_found
                        
                    templates.append(data)
                except Exception as e:
                    print(f"[!] Error parsing template {t_dir.name}: {e}")

    # 3. 读取主版本号
    pkg_json_file = base_dir / "package.json"
    version = "0.0.1"
    if pkg_json_file.exists():
        try:
            version = json.loads(pkg_json_file.read_text(encoding="utf-8")).get("version", "0.0.1")
        except:
            pass

    # 4. 聚合输出
    index_data = {
        "version": version,
        "totalRoles": len(roles),
        "totalTemplates": len(templates),
        "roles": roles,
        "templates": templates
    }

    out_index = knowledge_dir / "index.json"
    out_index.write_text(json.dumps(index_data, ensure_ascii=False, indent=2), encoding="utf-8")

    out_templates = knowledge_dir / "templates.json"
    out_templates.write_text(json.dumps({"templates": templates}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 60)
    print("  KnowMe CareerForge — Knowledge Index Built Successfully!")
    print(f"  Indexed Roles     : {len(roles)}")
    print(f"  Indexed Templates : {len(templates)}")
    print(f"  Output Registry   : {out_index.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    build_knowledge_index()
