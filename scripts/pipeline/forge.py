#!/usr/bin/env python3
"""
KnowMe CareerForge — Unified End-to-End Forge Engine
一键打通：代码仓事实挖掘 (repo-to-resume) ➔ JD 深度解析 ➔ 多维模板检索 ➔ HTML 工作区装配 ➔ Dual-QA 质检 ➔ 确定性 PDF 导出。
"""

import sys, os, json, argparse, subprocess
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — One-Shot Unified Forge Engine")
    parser.add_argument("--repo", "-r", default=".", help="Target code repository path (default: current directory)")
    parser.add_argument("--role", help="Target job title / role (e.g. 'AI Agent Engineer', '资深前端专家')")
    parser.add_argument("--jd", help="Path to JD file or raw JD text")
    parser.add_argument("--template", "-t", default="minimal", help="Template ID (minimal, modern, executive, classic)")
    parser.add_argument("--name", help="Candidate full name override")
    parser.add_argument("--email", help="Candidate email override")
    parser.add_argument("--phone", help="Candidate phone override")
    parser.add_argument("--output", "-o", default="workspace/resume.pdf", help="Output PDF file path")
    parser.add_argument("--html-output", default="workspace/resume.html", help="Intermediate working canvas HTML path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (compact JSON output for AI Agent)")

    args = parser.parse_args()
    root = get_project_root()
    scripts_dir = root / "scripts"

    if not args.quiet:
        print("==============================================================")
        print("  KnowMe CareerForge — One-Shot Resume Engineering Pipeline")
        print(f"  Target Role : {args.role or 'Auto-Detect'}")
        print(f"  Repo Source : {args.repo}")
        print(f"  Template    : {args.template}")
        print("==============================================================")

    # 1. 证据挖掘 (Stage 1: Evidence Mining)
    evidence_json = Path("workspace/evidence-master.json")
    
    extract_script = scripts_dir / "evidence" / "extract-evidence.py"
    if not extract_script.exists():
        extract_script = scripts_dir / "extract-evidence.py"

    evidence_cmd = [sys.executable, str(extract_script), "--repo", args.repo, "--output", str(evidence_json), "--quiet"]
    if args.name: evidence_cmd.extend(["--name", args.name])
    if args.role: evidence_cmd.extend(["--role", args.role])
    if args.email: evidence_cmd.extend(["--email", args.email])
    if args.phone: evidence_cmd.extend(["--phone", args.phone])

    subprocess.run(evidence_cmd, check=True)
    if not args.quiet:
        print("[✓] Stage 1: Codebase evidence mined -> workspace/evidence-master.json")

    # 2. JD 分析与关键词提取 (Stage 2: JD Analysis)
    keywords = []
    if args.jd:
        try:
            analyze_script = scripts_dir / "evidence" / "analyze-jd.py"
            if not analyze_script.exists():
                analyze_script = scripts_dir / "analyze-jd.py"

            jd_cmd = [sys.executable, str(analyze_script)]
            if Path(args.jd).exists():
                jd_cmd.extend(["--jd", args.jd])
            else:
                jd_cmd.extend(["--text", args.jd])
            jd_res = subprocess.run(jd_cmd, stdout=subprocess.PIPE, text=True, check=True)
            for line in jd_res.stdout.splitlines():
                if "Must-have Skills" in line or "Detected" in line:
                    parts = line.split(":")[-1].strip().split(",")
                    keywords.extend([p.strip() for p in parts if p.strip()])
        except Exception:
            pass

    # 3. 模板装配到工作区 (Stage 3 & 4: Template Instantiation)
    kw_arg = ",".join(keywords[:8]) if keywords else "TypeScript,Playwright,Python,Docker"
    
    instantiate_script = scripts_dir / "template" / "instantiate-resume.py"
    if not instantiate_script.exists():
        instantiate_script = scripts_dir / "instantiate-resume.py"

    instantiate_cmd = [
        sys.executable, str(instantiate_script),
        "--template", args.template,
        "--profile", str(evidence_json),
        "--keywords", kw_arg,
        "--output", args.html_output
    ]
    subprocess.run(instantiate_cmd, stdout=subprocess.DEVNULL if args.quiet else None, check=True)
    if not args.quiet:
        print(f"[✓] Stage 2: HTML Working Canvas instantiated -> {args.html_output}")

    # 4. 质检与自愈校验 (Stage 5: Dual QA Validation)
    val_script = scripts_dir / "validation" / "validate-resume.py"
    if not val_script.exists():
        val_script = scripts_dir / "validate-resume.py"

    validator_cmd = [
        sys.executable, str(val_script),
        args.html_output
    ]
    subprocess.run(validator_cmd, stdout=subprocess.DEVNULL if args.quiet else None, check=True)
    if not args.quiet:
        print("[✓] Stage 3: Dual QA Validation Passed 100%")

    # 5. 确定性渲染导出 PDF (Stage 6: PDF Export)
    render_script = scripts_dir / "rendering" / "render-pdf.py"
    if not render_script.exists():
        render_script = scripts_dir / "render-pdf.py"

    render_cmd = [
        sys.executable, str(render_script),
        args.html_output, args.output
    ]
    if args.quiet:
        render_cmd.append("--quiet")
    subprocess.run(render_cmd, check=True)

    if not args.quiet:
        print("==============================================================")
        print(f"  [✓] ALL STAGES COMPLETED SUCCESSFULLY!")
        print(f"  HTML Working Canvas : {Path(args.html_output).resolve()}")
        print(f"  Final Verified PDF  : {Path(args.output).resolve()}")
        print("==============================================================")
    else:
        result = {
            "status": "SUCCESS",
            "htmlCanvas": str(Path(args.html_output).resolve()),
            "pdfDelivery": str(Path(args.output).resolve()),
            "evidenceProfile": str(evidence_json.resolve()),
            "templateUsed": args.template
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
