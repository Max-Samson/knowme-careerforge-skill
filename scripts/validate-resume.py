#!/usr/bin/env python3
"""
KnowMe CareerForge — Resume Validation Engine (Layout, Schema & ATS Compliance)
验证 HTML 工作区简历的语义结构、Design Tokens 完整度与单页/双页排版合规性。
"""

import sys, os, json, argparse, re
from pathlib import Path

def validate_resume_html(html_path: str, expected_pages: int = 1) -> dict:
    p = Path(html_path)
    if not p.exists():
        # 尝试相对于脚本目录上一级
        alt = Path(__file__).resolve().parent.parent / html_path
        if alt.exists():
            p = alt
        else:
            return {
                "status": "FAIL",
                "file": html_path,
                "expectedPages": expected_pages,
                "checks": {},
                "errors": [f"HTML file not found at: {html_path}"],
                "warnings": []
            }

    content = p.read_text(encoding="utf-8")
    errors = []
    warnings = []
    checks = {}

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
        "--resume-font-size-body"
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

    # 6. 单页高度预估 (剔除 <style> 后的实际可见文字量)
    body_text_only = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    visible_text = re.sub(r'<[^>]+>', '', body_text_only).strip()
    char_count = len(re.sub(r'\s+', ' ', visible_text))

    density_status = "OPTIMAL"
    if expected_pages == 1:
        if char_count > 1500:
            warnings.append(f"Visible text volume ({char_count} chars) is high for a single-page resume; risk of overflow.")
            density_status = "HIGH_RISK_OVERFLOW"
        elif char_count < 400:
            warnings.append(f"Visible text volume ({char_count} chars) is low for a single-page resume; canvas may appear sparse.")
            density_status = "UNDERFLOW"

    checks["char_count"] = char_count
    checks["density_status"] = density_status

    passed = len(errors) == 0

    return {
        "status": "PASS" if passed else "FAIL",
        "file": str(p.resolve()),
        "expectedPages": expected_pages,
        "checks": checks,
        "errors": errors,
        "warnings": warnings
    }

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Resume Validator")
    parser.add_argument("--html", "-i", default="workspace/resume.html", help="Path to resume HTML (default: workspace/resume.html)")
    parser.add_argument("--expected-pages", "-p", type=int, default=1, help="Expected page count (default: 1)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    result = validate_resume_html(args.html, args.expected_pages)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=" * 70)
    print(f"  KnowMe CareerForge — Resume Validation: {result['status']}")
    print(f"  Target File    : {result['file']}")
    print(f"  Expected Pages : {result['expectedPages']}")
    print(f"  Text Density   : {result.get('checks', {}).get('density_status', 'N/A')} ({result.get('checks', {}).get('char_count', 0)} visible chars)")
    print(f"  Sections Found : {', '.join(result.get('checks', {}).get('detected_sections', []))}")

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
