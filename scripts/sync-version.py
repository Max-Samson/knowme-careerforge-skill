#!/usr/bin/env python3
"""
KnowMe CareerForge — Version Synchronization Engine
将项目根版本号统一同步至 package.json, pyproject.toml, skill.json 与 cli/package.json。
"""

import sys, os, json, re, argparse
from pathlib import Path

def sync_version(new_version: str):
    base_dir = Path(__file__).resolve().parent.parent
    print("==============================================================")
    print(f"  KnowMe CareerForge — Synchronizing Version to v{new_version}")
    print("==============================================================")

    # 1. Update package.json
    pkg_json_path = base_dir / "package.json"
    if pkg_json_path.exists():
        data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
        data["version"] = new_version
        pkg_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced package.json -> {new_version}")

    # 2. Update cli/package.json
    cli_pkg_path = base_dir / "cli" / "package.json"
    if cli_pkg_path.exists():
        data = json.loads(cli_pkg_path.read_text(encoding="utf-8"))
        data["version"] = new_version
        cli_pkg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced cli/package.json -> {new_version}")

    # 3. Update skill.json
    skill_json_path = base_dir / "skill.json"
    if skill_json_path.exists():
        data = json.loads(skill_json_path.read_text(encoding="utf-8"))
        data["version"] = new_version
        skill_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced skill.json -> {new_version}")

    # 4. Update pyproject.toml
    pyproj_path = base_dir / "pyproject.toml"
    if pyproj_path.exists():
        text = pyproj_path.read_text(encoding="utf-8")
        new_text = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', text)
        pyproj_path.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced pyproject.toml -> {new_version}")

    print("\n[✓] All package versions successfully synchronized!")

def main():
    parser = argparse.ArgumentParser(description="Synchronize project version")
    parser.add_argument("version", nargs="?", default="1.0.0", help="New semantic version (e.g. 1.0.1)")
    args = parser.parse_args()
    sync_version(args.version)

if __name__ == "__main__":
    main()
