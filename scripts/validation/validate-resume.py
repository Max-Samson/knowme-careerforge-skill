#!/usr/bin/env python3
"""
KnowMe CareerForge — Resume Validation Engine (Layout, Schema & ATS Compliance)
验证 HTML 工作区简历的语义结构、Design Tokens 完整度与单页/双页排版合规性。
"""

import sys, os, json, argparse, re
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def validate_resume_html(html_path: str, expected_pages: int = 1) -> dict:
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
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()
    target_html = args.html or args.path
    result = validate_resume_html(target_html, expected_pages=args.expected_pages)
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
