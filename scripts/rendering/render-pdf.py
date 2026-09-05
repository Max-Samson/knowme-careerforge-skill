#!/usr/bin/env python3
"""Render and verify a fresh PDF through browser-engine.js before publication."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_engine import run, exit_code


def render_pdf(html_path_str, pdf_path_str, quiet=False, expected_pages=1, auto_heal=False):
    result = run(html_path_str, expected_pages=expected_pages,
                 auto_heal=auto_heal, output_pdf=pdf_path_str)
    if result["status"] != "PASS":
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return Path(pdf_path_str).resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="?", default="workspace/resume.html")
    parser.add_argument("pdf", nargs="?", default="workspace/resume.pdf")
    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")
    parser.add_argument("--expected-pages", "-p", type=int, default=1)
    parser.add_argument("--auto-heal", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.input or args.html, expected_pages=args.expected_pages,
                 auto_heal=args.auto_heal, output_pdf=args.output or args.pdf)
    print(json.dumps(result, ensure_ascii=False))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
