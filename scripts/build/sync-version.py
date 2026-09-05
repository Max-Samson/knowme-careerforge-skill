#!/usr/bin/env python3
"""
KnowMe CareerForge — Version Synchronization Engine
将项目根版本号统一同步至 package.json, pyproject.toml, skill.json, cli/package.json, npm 锁文件, SKILL.md, agents/*, CLI 与知识索引。
"""

import sys, os, json, re, argparse
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def sync_version(new_version: str):
    base_dir = get_project_root()
    # 去除可能传入的 'v' 前缀
    semver = new_version.removeprefix("v")
    core = r"(?:0|[1-9][0-9]*)"
    prerelease = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    if not re.fullmatch(rf"{core}\.{core}\.{core}(?:-{prerelease}(?:\.{prerelease})*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", semver):
        raise ValueError(f"Invalid semantic version: {new_version}")

    print("==============================================================")
    print(f"  KnowMe CareerForge — Synchronizing Version to v{semver}")
    print("==============================================================")

    # 1. Update package.json
    pkg_json_path = base_dir / "package.json"
    if pkg_json_path.exists():
        data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
        data["version"] = semver
        pkg_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced package.json -> {semver}")

    # 2. Update cli/package.json
    cli_pkg_path = base_dir / "cli" / "package.json"
    if cli_pkg_path.exists():
        data = json.loads(cli_pkg_path.read_text(encoding="utf-8"))
        data["version"] = semver
        cli_pkg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced cli/package.json -> {semver}")

    # Lockfiles carry the package version separately from dependency versions.
    for relative in ("package-lock.json", "cli/package-lock.json"):
        lock_path = base_dir / relative
        if lock_path.exists():
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            data["version"] = semver
            if "" in data.get("packages", {}):
                data["packages"][""]["version"] = semver
            lock_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[✓] Synced {relative} -> {semver}")

    # 3. Update skill.json
    skill_json_path = base_dir / "skill.json"
    if skill_json_path.exists():
        data = json.loads(skill_json_path.read_text(encoding="utf-8"))
        data["version"] = semver
        skill_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[✓] Synced skill.json -> {semver}")

    # 4. Update pyproject.toml
    pyproj_path = base_dir / "pyproject.toml"
    if pyproj_path.exists():
        text = pyproj_path.read_text(encoding="utf-8")
        new_text = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{semver}"', text)
        pyproj_path.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced pyproject.toml -> {semver}")

    # 5. Update SKILL.md
    skill_md_path = base_dir / "SKILL.md"
    if skill_md_path.exists():
        text = skill_md_path.read_text(encoding="utf-8")
        new_text = re.sub(r'(?m)^(\s*version:)[ \t]*[^\r\n]+$', lambda m: f'{m[1]} {semver}', text)
        skill_md_path.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced SKILL.md -> {semver}")

    # 6. Update agents/codex/knowme-careerforge.yaml
    codex_yaml = base_dir / "agents" / "codex" / "knowme-careerforge.yaml"
    if codex_yaml.exists():
        text = codex_yaml.read_text(encoding="utf-8")
        new_text = re.sub(r'(?m)^(\s*version:)[ \t]*[^\r\n]+$', lambda m: f'{m[1]} {semver}', text)
        codex_yaml.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced agents/codex/knowme-careerforge.yaml -> {semver}")

    # 7. Update agents/opencode/skill.yaml
    opencode_yaml = base_dir / "agents" / "opencode" / "skill.yaml"
    if opencode_yaml.exists():
        text = opencode_yaml.read_text(encoding="utf-8")
        new_text = re.sub(r'(?m)^(\s*version:)[ \t]*[^\r\n]+$', lambda m: f'{m[1]} {semver}', text)
        opencode_yaml.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced agents/opencode/skill.yaml -> {semver}")
    # 8. Update cli/src/index.ts fallback version
    cli_ts_path = base_dir / "cli" / "src" / "index.ts"
    if cli_ts_path.exists():
        text = cli_ts_path.read_text(encoding="utf-8")
        new_text = re.sub(r"return\s+data\.version\s*\|\|\s*'[^']+'", f"return data.version || '{semver}'", text)
        new_text = re.sub(r"return\s+'\d+\.\d+\.\d+[^']*'\s*;", f"return '{semver}';", new_text)
        cli_ts_path.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced cli/src/index.ts -> {semver}")


    # 9. Update scripts/Agent.md
    agent_md = base_dir / "scripts" / "Agent.md"
    if agent_md.exists():
        text = agent_md.read_text(encoding="utf-8")
        new_text = re.sub(r'版本[：:]\s*v[\d.]+(?:-[\w.]+)?', f'版本：v{semver}', text)
        agent_md.write_text(new_text, encoding="utf-8")
        print(f"[✓] Synced scripts/Agent.md -> v{semver}")

    # 10. Recompile knowledge index to update index.json version
    kb_script = base_dir / "scripts" / "build" / "build-knowledge.py"
    if kb_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(kb_script)], stdout=subprocess.DEVNULL, check=True)
        print(f"[✓] Recompiled knowledge index -> v{semver}")

    print("\n[✓] All package versions successfully synchronized!")

def main():
    parser = argparse.ArgumentParser(description="Synchronize project version")
    parser.add_argument("version", help="Required target semantic version (e.g. 0.0.6)")
    args = parser.parse_args()
    try:
        sync_version(args.version)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Version synchronization failed: {error}\n")

if __name__ == "__main__":
    main()
