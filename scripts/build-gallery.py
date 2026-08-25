#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Gallery Builder
扫描验证 src/templates/ 核心模板，生成 output/templates_gallery/ 静态可视化画廊。
"""

import os, sys, json, re
from pathlib import Path

def build_gallery():
    base_dir = Path(__file__).resolve().parent.parent
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
            html_raw = html_file.read_text(encoding="utf-8")
            css_raw = css_file.read_text(encoding="utf-8")

            # 生成单文件自包含预览页面
            inlined_preview = html_raw.replace(
                '<link rel="stylesheet" href="style.css">',
                f'<style>\n{css_raw}\n  </style>'
            )

            preview_path = gallery_dir / f"{meta['id']}.html"
            preview_path.write_text(inlined_preview, encoding="utf-8")

            gallery_items.append({
                "id": meta["id"],
                "name": meta.get("name", meta["id"]),
                "style": meta.get("style", "custom"),
                "category": meta.get("roleCategory", "engineering-ai"),
                "accent": meta.get("visualStyle", {}).get("accentColor", "#2563eb"),
                "targetPages": meta.get("layout", {}).get("targetPages", 1),
                "density": meta.get("layout", {}).get("density", "balanced"),
                "supported": meta.get("supportedRoles", []),
                "previewUrl": f"{meta['id']}.html"
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
  <title>KnowMe CareerForge — 核心基准模板画廊</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --accent: #38bdf8;
      --text: #f8fafc;
      --muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 32px 20px;
    }}
    .container {{
      max-width: 1360px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      margin-bottom: 32px;
    }}
    h1 {{ font-size: 26px; color: var(--accent); margin-bottom: 8px; font-weight: 800; }}
    p.subtitle {{ color: var(--muted); font-size: 14px; max-width: 680px; margin: 0 auto; line-height: 1.5; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 24px;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--text);
    }}
    .badge {{
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 12px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .meta-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 13px;
      color: var(--muted);
    }}
    .meta-item strong {{
      color: var(--text);
    }}
    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 4px;
    }}
    .tag {{
      background: #334155;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      color: #e2e8f0;
    }}
    .frame-wrapper {{
      width: 100%;
      height: 480px;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: #ffffff;
      position: relative;
    }}
    iframe {{
      width: 210mm;
      height: 297mm;
      border: none;
      transform: scale(0.48);
      transform-origin: top left;
      position: absolute;
      top: 0;
      left: 0;
      pointer-events: none;
    }}
    .btn {{
      display: inline-block;
      text-align: center;
      background: var(--accent);
      color: #0f172a;
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
      transition: opacity 0.2s;
    }}
    .btn:hover {{ opacity: 0.9; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>KnowMe CareerForge — 核心基准模板画廊</h1>
      <p class="subtitle">面向 AI Agent 的确定性 HTML 简历设计工作场。所有模板均遵循 A4 绝对印刷几何与 CSS Design Tokens 规范。</p>
    </div>
    <div class="grid">
"""

    for item in gallery_items:
        tags_html = "".join([f'<span class="tag">{r}</span>' for r in item['supported'][:5]])
        gallery_html += f"""
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">{item['name']}</div>
            <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">ID: <code>{item['id']}</code></div>
          </div>
          <span class="badge">{item['style']}</span>
        </div>
        <div class="meta-list">
          <div class="meta-item"><strong>类别：</strong>{item['category']} | <strong>页数：</strong>{item['targetPages']} 页 | <strong>密度：</strong>{item['density']}</div>
          <div class="meta-item"><strong>支持岗位：</strong></div>
          <div class="tags">{tags_html}</div>
        </div>
        <div class="frame-wrapper">
          <iframe src="{item['previewUrl']}"></iframe>
        </div>
        <a href="{item['previewUrl']}" target="_blank" class="btn">打开独立预览 (A4 全尺寸)</a>
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
