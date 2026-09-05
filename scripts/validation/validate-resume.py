#!/usr/bin/env python3
"""
KnowMe CareerForge — Resume Validation Engine (Layout, Schema & ATS Compliance)
验证 HTML 工作区简历的语义结构、Design Tokens 完整度与单页/双页排版合规性。
"""

import sys, os, json, argparse, re, shutil, subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def update_root_token(html_path: Path, token_name: str, token_value: str) -> bool:
    """Update or insert a CSS variable in the :root declaration of the HTML canvas."""
    content = html_path.read_text(encoding="utf-8")
    token_pattern = re.compile(rf'({re.escape(token_name)}\s*:\s*)([^;]+)(;)')
    if token_pattern.search(content):
        new_content = token_pattern.sub(rf'\g<1>{token_value}\g<3>', content)
        html_path.write_text(new_content, encoding="utf-8")
        return True
    else:
        root_pattern = re.compile(r'(:root\s*\{)', re.IGNORECASE)
        if root_pattern.search(content):
            new_content = root_pattern.sub(rf'\g<1>\n  {token_name}: {token_value};', content, count=1)
            html_path.write_text(new_content, encoding="utf-8")
            return True
    return False

def _estimate_box_model_height(html_path: Path) -> float:
    """Pure-Python box-model physical height fallback when headless browser is unavailable."""
    content = html_path.read_text(encoding="utf-8")
    
    # Extract current tokens
    def get_token_pt(tok: str, default_pt: float) -> float:
        m = re.search(rf'{re.escape(tok)}\s*:\s*([\d\.]+)pt', content)
        return float(m.group(1)) if m else default_pt

    def get_token_num(tok: str, default_num: float) -> float:
        m = re.search(rf'{re.escape(tok)}\s*:\s*([\d\.]+)', content)
        return float(m.group(1)) if m else default_num

    space_sec_pt = get_token_pt("--resume-space-section", 11.0)
    space_item_pt = get_token_pt("--resume-space-item", 7.5)
    space_bullet_pt = get_token_pt("--resume-space-bullet", 2.0)
    font_size_pt = get_token_pt("--resume-font-size-body", 9.0)
    line_height = get_token_num("--resume-line-height-body", 1.42)

    # 1pt = 1.333px at 96DPI
    pt_to_px = 1.3333
    base_padding_px = 90.0  # ~12mm top + 12mm bottom
    header_px = 110.0

    sec_count = len(re.findall(r'<section[^>]*class="[^"]*resume-section[^"]*"', content)) or 4
    item_count = len(re.findall(r'class="[^"]*(?:experience|project|education)-item[^"]*"', content)) or 5
    bullet_count = len(re.findall(r'<li[^>]*>', content)) or 10

    body_text_only = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    visible_text = re.sub(r'<[^>]+>', '', body_text_only).strip()
    char_count = len(re.sub(r'\s+', ' ', visible_text))
    line_count = max(bullet_count, int(char_count / 42.0))

    h_sec = sec_count * (space_sec_pt * pt_to_px + 28.0)
    h_item = item_count * (space_item_pt * pt_to_px)
    h_bullet = bullet_count * (space_bullet_pt * pt_to_px)
    h_text = line_count * (font_size_pt * pt_to_px * line_height)

    return round(base_padding_px + header_px + h_sec + h_item + h_bullet + h_text, 1)

def measure_dom_height(html_path: Path) -> Tuple[float, List[Dict[str, Any]]]:
    """Measure DOM rendered height using headless browser or fall back to box model."""
    root = get_project_root()
    measure_js = root / "scripts" / "validation" / "measure-dom.js"
    if not measure_js.exists():
        alt = html_path.resolve().parent.parent / "scripts" / "validation" / "measure-dom.js"
        if alt.exists():
            measure_js = alt

    if shutil.which("node") and measure_js.exists():
        try:
            res = subprocess.run(
                ["node", str(measure_js), str(html_path.resolve())],
                capture_output=True,
                text=True,
                timeout=12
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout.strip())
                return float(data.get("actualHeightPx", 1122.5)), data.get("overflowItems", [])
        except Exception:
            pass

    # Fallback to pure-Python box-model calculation
    est_h = _estimate_box_model_height(html_path)
    return est_h, []

def generate_content_condense_advisory(html_path: Path, delta_px: float, overflow_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Generate targeted content condensation advisory for AI Agent when physical height still overflows."""
    content = html_path.read_text(encoding="utf-8")
    est_lines = max(1, int(round(delta_px / 18.0)))
    est_chars = est_lines * 45

    suggested_nodes = []
    if overflow_items:
        for it in overflow_items:
            if it.get("selector"):
                suggested_nodes.append(it.get("selector"))

    if not suggested_nodes:
        if 'id="projects"' in content:
            suggested_nodes.append("#projects .project-item:last-child")
        if 'id="experience"' in content:
            suggested_nodes.append("#experience .experience-item:last-child .bullet-list li:last-child")
        if 'id="skills"' in content:
            suggested_nodes.append("#skills .skill-row:last-child")

    return {
        "overflowDeltaPx": round(delta_px, 1),
        "estimatedExcessLines": est_lines,
        "estimatedExcessChars": est_chars,
        "targetNodes": list(dict.fromkeys(suggested_nodes)),
        "guidance": f"物理排版溢出 {round(delta_px, 1)}px。建议对 {', '.join(suggested_nodes[:2])} 精简约 {est_chars} 字（约 {est_lines} 行文本），或精简至近 2~3 段核心经历。"
    }

def auto_heal_resume(html_path: Path, max_pages: int = 1) -> Dict[str, Any]:
    """
    Heuristic Token Auto-Healing Algorithm (ADR-0005)
    Ladder:
      1. Section Spacing: 10.5pt -> 9.5pt -> 8.5pt
      2. Item & Bullet Spacing: (7.0pt, 2.5pt) -> (6.0pt, 2.0pt) -> (5.0pt, 1.5pt)
      3. Typography Scale & Line Height: (9.0pt, 1.42) -> (8.8pt, 1.38)
      4. Content Condense Advisory if still overflowing
    """
    target_height = max_pages * 1122.5  # A4 standard at 96 DPI
    current_height, overflow_items = measure_dom_height(html_path)
    initial_height = current_height
    tuned_tokens: Dict[str, str] = {}

    # 2px floating-point rounding tolerance
    if current_height <= target_height + 2:
        return {
            "healed": True,
            "initialHeight": initial_height,
            "finalHeight": current_height,
            "targetHeight": target_height,
            "stage": "none",
            "iterations": 0,
            "tunedTokens": tuned_tokens,
            "advisory": None
        }

    iterations = 0

    # 阶段 1: 压缩模块间距 (Section Spacing)
    for space_sec in [10.5, 9.5, 8.5]:
        iterations += 1
        update_root_token(html_path, "--resume-space-section", f"{space_sec}pt")
        tuned_tokens["--resume-space-section"] = f"{space_sec}pt"
        current_height, overflow_items = measure_dom_height(html_path)
        if current_height <= target_height + 2:
            return {
                "healed": True,
                "initialHeight": initial_height,
                "finalHeight": current_height,
                "targetHeight": target_height,
                "stage": "section_spacing",
                "iterations": iterations,
                "tunedTokens": tuned_tokens,
                "advisory": None
            }

    # 阶段 2: 压缩条目与列表项间距 (Item & Bullet Spacing)
    for space_item, space_bullet in [(7.0, 2.5), (6.0, 2.0), (5.0, 1.5)]:
        iterations += 1
        update_root_token(html_path, "--resume-space-item", f"{space_item}pt")
        update_root_token(html_path, "--resume-space-bullet", f"{space_bullet}pt")
        tuned_tokens["--resume-space-item"] = f"{space_item}pt"
        tuned_tokens["--resume-space-bullet"] = f"{space_bullet}pt"
        current_height, overflow_items = measure_dom_height(html_path)
        if current_height <= target_height + 2:
            return {
                "healed": True,
                "initialHeight": initial_height,
                "finalHeight": current_height,
                "targetHeight": target_height,
                "stage": "item_bullet_spacing",
                "iterations": iterations,
                "tunedTokens": tuned_tokens,
                "advisory": None
            }

    # 阶段 3: 微调字号与正文行高 (Typography Scale - 保持物理可读底线 >= 8.8pt)
    for font_size, line_height in [(9.0, 1.42), (8.8, 1.38)]:
        iterations += 1
        update_root_token(html_path, "--resume-font-size-body", f"{font_size}pt")
        update_root_token(html_path, "--resume-line-height-body", f"{line_height}")
        tuned_tokens["--resume-font-size-body"] = f"{font_size}pt"
        tuned_tokens["--resume-line-height-body"] = f"{line_height}"
        current_height, overflow_items = measure_dom_height(html_path)
        if current_height <= target_height + 2:
            return {
                "healed": True,
                "initialHeight": initial_height,
                "finalHeight": current_height,
                "targetHeight": target_height,
                "stage": "typography",
                "iterations": iterations,
                "tunedTokens": tuned_tokens,
                "advisory": None
            }

    # 阶段 4: 若仍溢出，计算具体超出的高度与节点选择器，输出精简文本指引
    delta_px = current_height - target_height
    advisory = generate_content_condense_advisory(html_path, delta_px, overflow_items)
    return {
        "healed": False,
        "initialHeight": initial_height,
        "finalHeight": current_height,
        "targetHeight": target_height,
        "overflowDeltaPx": round(delta_px, 1),
        "stage": "overflow_advisory",
        "iterations": iterations,
        "tunedTokens": tuned_tokens,
        "advisory": advisory
    }

def validate_resume_html(html_path: str, expected_pages: int = 1, auto_heal: bool = False) -> dict:
    p = Path(html_path)
    if not p.exists():
        root = get_project_root()
        alt = root / html_path
        if alt.exists():
            p = alt
        else:
            return {
                "status": "FAIL",
                "file": str(p),
                "errors": [f"File not found: {html_path}"],
                "warnings": [],
                "checks": {}
            }

    content = p.read_text(encoding="utf-8")
    errors = []
    warnings = []
    checks = {}

    # 0. 启发式自动自愈 (Heuristic Auto-Healing if requested)
    if auto_heal:
        heal_res = auto_heal_resume(p, max_pages=expected_pages)
        checks["auto_heal"] = heal_res
        checks["dom_height_px"] = heal_res["finalHeight"]
        checks["target_height_px"] = heal_res["targetHeight"]
        
        if heal_res["healed"]:
            checks["auto_heal_status"] = "PASS"
            if heal_res["iterations"] > 0:
                warnings.append(
                    f"Auto-healed DOM overflow via {heal_res['stage']} (reduced to {heal_res['finalHeight']}px <= {heal_res['targetHeight']}px, tuned: {heal_res['tunedTokens']})"
                )
        else:
            checks["auto_heal_status"] = "FAIL"
            errors.append(
                f"DOM height overflow ({heal_res['finalHeight']}px > {heal_res['targetHeight']}px by {heal_res['overflowDeltaPx']}px). {heal_res['advisory']['guidance']}"
            )
        
        # Reload content after token tuning
        content = p.read_text(encoding="utf-8")
    # 1. 检查语义化容器
    if '<div class="resume-page"' not in content and "<div class='resume-page'" not in content:
        errors.append("Missing root container <div class='resume-page'>")
    else:
        checks["root_container"] = "PASS"

    # 2. 检查基本信息字段
    if 'candidate-name' not in content:
        errors.append("Missing candidate name element (.candidate-name)")
    else:
        checks["candidate_name"] = "PASS"

    # 3. 检查 Design Tokens (:root CSS 变量)
    required_tokens = [
        "--resume-page-width",
        "--resume-page-min-height",
        "--resume-font-size-body",
        "--resume-space-section",
        "--resume-color-primary"
    ]
    missing_tokens = []
    for token in required_tokens:
        if token not in content:
            missing_tokens.append(token)

    if missing_tokens:
        warnings.append(f"Missing recommended CSS Design Tokens: {', '.join(missing_tokens)}")
    else:
        checks["design_tokens"] = "PASS"

    # 4. 检查打印分页规则
    if "@page" not in content:
        warnings.append("Missing @page print declaration in CSS")
    if "page-break-after" not in content and "break-after" not in content:
        warnings.append("Missing page-break-after CSS rules for multi-page/A4 constraints")

    # 5. 检查核心内容模块
    sections = ["experience", "projects", "skills", "education"]
    detected_sections = []
    for s in sections:
        if f'id="{s}"' in content or f"id='{s}'" in content or s in content.lower():
            detected_sections.append(s)

    checks["detected_sections"] = detected_sections

    # 6. 单页高度预估 (可见文字量)
    body_text_only = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    visible_text = re.sub(r'<[^>]+>', '', body_text_only).strip()
    char_count = len(re.sub(r'\s+', ' ', visible_text))

    density_status = "OPTIMAL"
    if expected_pages == 1:
        if char_count > 1600:
            warnings.append(f"High text density for 1 page: {char_count} chars (recommend trimming or reducing spacing tokens)")
            density_status = "OVERFLOW_RISK"
        elif char_count < 300:
            warnings.append(f"Low content volume for 1 page: {char_count} chars")
            density_status = "UNDERFLOW"

    checks["char_count"] = char_count
    checks["density_status"] = density_status

    passed = len(errors) == 0

    return {
        "status": "PASS" if passed else "FAIL",
        "file": str(p.resolve()),
        "expectedPages": expected_pages,
        "errors": errors,
        "warnings": warnings,
        "checks": checks
    }

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Resume Validator")
    parser.add_argument("path", nargs="?", default="workspace/resume.html", help="Path to resume.html")
    parser.add_argument("--html", help="Path to resume.html (named)")
    parser.add_argument("--expected-pages", "-p", type=int, default=1, help="Expected target pages (1 or 2)")
    parser.add_argument("--auto-heal", action="store_true", help="Enable heuristic token auto-healing to eliminate DOM height overflow")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()
    target_html = args.html or args.path
    result = validate_resume_html(target_html, expected_pages=args.expected_pages, auto_heal=args.auto_heal)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=" * 70)
    print(f"  KnowMe CareerForge — Resume Validation: {result['status']}")
    print(f"  Target File    : {result['file']}")
    print(f"  Expected Pages : {result['expectedPages']}")
    print(f"  Text Density   : {result.get('checks', {}).get('density_status', 'N/A')} ({result.get('checks', {}).get('char_count', 0)} visible chars)")
    print(f"  Sections Found : {', '.join(result.get('checks', {}).get('detected_sections', []))}")
    if "auto_heal" in result.get("checks", {}):
        ah = result["checks"]["auto_heal"]
        stage_str = ah.get("stage", "none")
        print(f"  Auto-Heal      : {result['checks'].get('auto_heal_status')} (Stage: {stage_str}, Iterations: {ah.get('iterations', 0)}, Final Height: {ah.get('finalHeight')}px / Target: {ah.get('targetHeight')}px)")
        if ah.get("tunedTokens"):
            print(f"  Tuned Tokens   : {json.dumps(ah.get('tunedTokens'))}")

    if result.get("errors"):
        print("\n[!] Errors:")
        for e in result["errors"]:
            print(f"  - ✗ {e}")

    if result.get("warnings"):
        print("\n[?] Warnings:")
        for w in result["warnings"]:
            print(f"  - ⚠️ {w}")

    print("=" * 70)
    if result["status"] != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()
