#!/usr/bin/env python3
"""
KnowMe CareerForge — Multi-Strategy Deterministic PDF Renderer
多策略自愈式 A4 PDF 渲染器：自动嗅探 Playwright、系统级 Chromium/Chrome/Edge/Brave 浏览器并实现零配置确定性导出。
"""

import sys, os, subprocess, platform, shutil, argparse
from pathlib import Path
from typing import Optional, List

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def find_system_browser() -> Optional[str]:
    system = platform.system()
    
    custom_bin = os.environ.get("CHROME_BIN") or os.environ.get("BROWSER_PATH")
    if custom_bin and Path(custom_bin).exists():
        return custom_bin

    candidates: List[str] = []
    
    if system == "Darwin":  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            str(Path.home() / "Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
    elif system == "Linux":
        candidates = [
            "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
            "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium", "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    elif system == "Windows":
        prog_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        prog_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        local_app = os.environ.get("LOCALAPPDATA", "")
        
        candidates = [
            os.path.join(prog_files, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(prog_files_x86, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(prog_files_x86, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(prog_files, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(local_app, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(local_app, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(local_app, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]

    for candidate in candidates:
        if candidate.startswith("/") or ":" in candidate:
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved

    return None

def render_via_playwright(html_path: Path, pdf_path: Path) -> bool:
    root = get_project_root()
    script_ts = root / "scripts" / "rendering" / "render-pdf.ts"
    if not script_ts.exists():
        script_ts = root / "scripts" / "render-pdf.ts"

    if script_ts.exists() and shutil.which("npx"):
        try:
            cmd = ["npx", "ts-node", str(script_ts), "--input", str(html_path), "--output", str(pdf_path)]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            if res.returncode == 0 and pdf_path.exists():
                return True
        except Exception:
            pass
    return False

def render_via_browser(browser_bin: str, html_path: Path, pdf_path: Path) -> bool:
    html_url = html_path.resolve().as_uri()
    cmd = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_url
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
        return pdf_path.exists() and pdf_path.stat().st_size > 0
    except Exception as e:
        print(f"[!] Browser render failed: {e}")
        return False

def render_pdf(html_path_str: str, pdf_path_str: str, quiet: bool = False) -> Path:
    html_path = Path(html_path_str).resolve()
    pdf_path = Path(pdf_path_str).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"Input HTML file does not exist: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    if not quiet:
        print("==============================================================")
        print("  KnowMe CareerForge — Multi-Strategy PDF Renderer")
        print(f"  Source Canvas : {html_path}")
        print(f"  Target PDF    : {pdf_path}")
        print("==============================================================")

    # Strategy 1: Playwright Headless
    if not quiet:
        print("[*] Strategy 1: Trying Playwright Headless Engine...")
    if render_via_playwright(html_path, pdf_path):
        if not quiet:
            print(f"[✓] Render Succeeded via Playwright -> {pdf_path}")
        return pdf_path

    # Strategy 2: System Installed Chromium/Chrome/Edge/Brave
    browser_bin = find_system_browser()
    if browser_bin:
        if not quiet:
            print(f"[*] Strategy 2: Found system browser at: {browser_bin}")
        if render_via_browser(browser_bin, html_path, pdf_path):
            if not quiet:
                print(f"[✓] Render Succeeded via System Browser -> {pdf_path}")
            return pdf_path

    raise RuntimeError("No suitable PDF rendering engine found. Please install Playwright or Google Chrome / Edge.")

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Multi-Strategy PDF Renderer")
    parser.add_argument("html", nargs="?", default="workspace/resume.html", help="Input HTML canvas path")
    parser.add_argument("pdf", nargs="?", default="workspace/resume.pdf", help="Output PDF path")
    parser.add_argument("--input", "-i", help="Input HTML (named option)")
    parser.add_argument("--output", "-o", help="Output PDF (named option)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet execution mode")

    args = parser.parse_args()
    input_html = args.input or args.html
    output_pdf = args.output or args.pdf

    try:
        render_pdf(input_html, output_pdf, quiet=args.quiet)
    except Exception as e:
        print(f"[✗] PDF Generation Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
