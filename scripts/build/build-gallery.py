#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Gallery Builder
扫描验证 src/templates/ 核心模板，生成 output/templates_gallery/ 静态可视化画廊。
"""

import os, sys, json, re
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def build_gallery():
    base_dir = get_project_root()
    templates_dir = base_dir / "src" / "templates"
    gallery_dir = base_dir / "output" / "templates_gallery"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    
    gallery_items = []

    print("==============================================================")
    print("  KnowMe CareerForge — Template Gallery Builder")
    print("==============================================================")

    for t_dir in sorted(templates_dir.iterdir()):
        if not t_dir.is_dir() or t_dir.name == "common":
            continue
            
        html_file = t_dir / "template.html"
        css_file = t_dir / "style.css"
        meta_file = t_dir / "metadata.json"

        if not html_file.exists() or not css_file.exists() or not meta_file.exists():
            print(f"[!] Skipping incomplete template: {t_dir.name}")
            continue

        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            html_content = html_file.read_text(encoding="utf-8")
            css_content = css_file.read_text(encoding="utf-8")

            # 编译内联单文件独立预览页面
            inlined_preview = html_content.replace(
                '<link rel="stylesheet" href="style.css">',
                f'<style>\n{css_content}\n  </style>'
            )

            preview_path = gallery_dir / f"{t_dir.name}.html"
            preview_path.write_text(inlined_preview, encoding="utf-8")

            gallery_items.append({
                "id": meta.get("id", t_dir.name),
                "name": meta.get("name", t_dir.name),
                "style": meta.get("style", "single-column"),
                "category": meta.get("roleCategory", "engineering-ai"),
                "tone": meta.get("visualStyle", {}).get("tone", "modern"),
                "accent": meta.get("visualStyle", {}).get("accentColor", "#2563eb"),
                "pages": meta.get("layout", {}).get("targetPages", 1),
                "density": meta.get("layout", {}).get("density", "balanced"),
                "atsTier": meta.get("atsScoreTier", "tier-1-optimal"),
                "previewFile": f"{t_dir.name}.html",
                "supported": meta.get("supportedRoles", [])
            })
            print(f"[✓] Generated Gallery Preview -> {preview_path.name}")
        except Exception as e:
            print(f"[✗] Error processing {t_dir.name}: {e}")

    # 生成主索引 index.html
    gallery_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KnowMe CareerForge — HTML Resume Template Gallery</title>
  <style>
    :root {{
      --primary: #0f172a;
      --secondary: #475569;
      --accent: #2563eb;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background-color: var(--bg);
      color: var(--primary);
      padding: 40px 20px;
      line-height: 1.5;
    }}
    .gallery-container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 40px;
    }}
    h1 {{
      font-size: 28px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: var(--secondary);
      font-size: 15px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      transition: transform 0.2s, box-shadow 0.2s;
      display: flex;
      flex-direction: column;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.1);
    }}
    .card-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      background: #f1f5f9;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .card-title {{
      font-size: 16px;
      font-weight: 700;
    }}
    .badge {{
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 9999px;
      background: #e2e8f0;
      color: var(--secondary);
      font-weight: 600;
    }}
    .badge.optimal {{
      background: #dcfce7;
      color: #166534;
    }}
    .preview-frame-wrapper {{
      height: 380px;
      overflow: hidden;
      position: relative;
      background: #e2e8f0;
    }}
    .preview-frame {{
      width: 210mm;
      height: 297mm;
      transform: scale(0.35);
      transform-origin: top left;
      border: none;
      pointer-events: none;
      background: #fff;
    }}
    .card-body {{
      padding: 16px 20px;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .meta-list {{
      font-size: 13px;
      color: var(--secondary);
      margin-bottom: 12px;
      line-height: 1.6;
    }}
    .tag-container {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-bottom: 16px;
    }}
    .tag {{
      font-size: 11px;
      background: #f1f5f9;
      color: #334155;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .btn {{
      display: block;
      text-align: center;
      padding: 8px 16px;
      background: var(--accent);
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      transition: background 0.2s;
    }}
    .btn:hover {{
      background: #1d4ed8;
    }}
  </style>
</head>
<body>
  <div class="gallery-container">
    <header>
      <h1>KnowMe CareerForge — Template Gallery</h1>
      <p class="subtitle">A4 Deterministic HTML Resume Templates with Design Tokens Calibration</p>
    </header>
    <div class="grid">
"""

    for item in gallery_items:
        tags_html = "".join([f'<span class="tag">{r}</span>' for r in item['supported'][:5]])
        gallery_html += f"""
      <div class="card">
        <div class="card-header">
          <span class="card-title">{item['name']}</span>
          <span class="badge optimal">ATS Tier 1</span>
        </div>
        <div class="preview-frame-wrapper">
          <iframe class="preview-frame" src="{item['previewFile']}"></iframe>
        </div>
        <div class="card-body">
          <div class="meta-list">
            <div><strong>Style:</strong> {item['style']}</div>
            <div><strong>Target:</strong> {item['pages']} page(s) ({item['density']} density)</div>
            <div><strong>Tone:</strong> {item['tone']}</div>
          </div>
          <div class="tag-container">
            {tags_html}
          </div>
          <a class="btn" href="{item['previewFile']}" target="_blank">Open Full A4 Preview ↗</a>
        </div>
      </div>
"""

    gallery_html += """
    </div>
  </div>
</body>
</html>
"""
    gallery_index = gallery_dir / "index.html"
    gallery_index.write_text(gallery_html, encoding="utf-8")
    print(f"\n[✓] Generated Gallery Master Index -> {gallery_index}")
    print("==============================================================")

if __name__ == "__main__":
    build_gallery()
