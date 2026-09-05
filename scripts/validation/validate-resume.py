#!/usr/bin/env python3
"""Validate print DOM and an actual temporary PDF through the shared engine."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rendering"))
from browser_engine import run, exit_code


def validate_resume_html(html_path, expected_pages=1, auto_heal=False):
    return run(html_path, expected_pages=expected_pages, auto_heal=auto_heal)


def auto_heal_resume(html_path, max_pages=1):
    result = validate_resume_html(html_path, max_pages, True)
    return {**result.get("checks", {}).get("auto_heal", {}),
            "healed": result["status"] == "PASS", "status": result["status"],
            "errors": result["errors"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="workspace/resume.html")
    parser.add_argument("--html")
    parser.add_argument("--expected-pages", "-p", type=int, default=1)
    parser.add_argument("--auto-heal", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_resume_html(args.html or args.path, args.expected_pages, args.auto_heal)
    print(json.dumps(result, ensure_ascii=False))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
