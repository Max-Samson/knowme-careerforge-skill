#!/usr/bin/env python3
"""
KnowMe CareerForge — Release & NPM Publishing Automation Script
自动化执行版本同步、知识库编译、画廊刷新、TypeScript 构建、测试验证与 NPM 打包检查。
"""

import sys, os, subprocess, json, re, argparse
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def run_command(cmd, cwd, desc):
    print(f"\n[+] {desc}...")
    proc = subprocess.run(cmd, shell=True, text=True, cwd=cwd, capture_output=True)
    if proc.returncode != 0:
        print(f"[✗] Failed at: {desc}")
        print(f"Error Output:\n{proc.stderr}\n{proc.stdout}")
        sys.exit(1)
    print(f"[✓] {desc} succeeded.")
    return proc.stdout

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Release & NPM Publish Helper")
    parser.add_argument("version", nargs="?", help="New semantic version to release (e.g. 1.0.1, 1.1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Perform build and test verification without publishing")
    parser.add_argument("--publish", action="store_true", help="Directly trigger npm publish --access public after verification")

    args = parser.parse_args()
    base_dir = get_project_root()

    # 1. 确定版本号
    pkg_file = base_dir / "package.json"
    current_version = "1.0.0"
    if pkg_file.exists():
        current_version = json.loads(pkg_file.read_text(encoding="utf-8")).get("version", "1.0.0")

    target_version = args.version or current_version

    if not re.match(r'^\d+\.\d+\.\d+(?:-[\w.]+)?$', target_version):
        print(f"[!] Invalid semantic version format: {target_version}. Expected format: X.Y.Z (e.g. 1.0.1)")
        sys.exit(1)

    print("==============================================================")
    print("  KnowMe CareerForge — NPM Build & Release Automation")
    print(f"  Current Version : {current_version}")
    print(f"  Target Version  : {target_version}")
    print(f"  Working Root    : {base_dir}")
    print("==============================================================")

    # 2. 同步多文件版本号
    if target_version != current_version or args.version:
        sync_script = base_dir / "scripts" / "build" / "sync-version.py"
        run_command(f"python3 {sync_script} {target_version}", base_dir, f"Synchronizing version to v{target_version}")

    # 3. 重新编译知识库索引
    build_kb = base_dir / "scripts" / "build" / "build-knowledge.py"
    run_command(f"python3 {build_kb}", base_dir, "Compiling Knowledge Base Index")

    # 4. 重新构建模板画廊
    build_gal = base_dir / "scripts" / "build" / "build-gallery.py"
    run_command(f"python3 {build_gal}", base_dir, "Building HTML Template Gallery")

    # 5. 编译 TypeScript CLI 产物
    run_command("npm run build", base_dir, "Compiling TypeScript CLI (tsc -> dist/)")

    # 6. 运行全链路自动化测试套件
    test_script = base_dir / "scripts" / "build" / "run-all-tests.py"
    run_command(f"python3 {test_script}", base_dir, "Running Full-Chain Test Suites")

    # 7. NPM 打包预检 (npm pack --dry-run)
    pack_output = run_command("npm pack --dry-run --json", base_dir, "Inspecting NPM Package Files")

    try:
        pack_data = json.loads(pack_output)
        if isinstance(pack_data, list) and len(pack_data) > 0:
            files_count = pack_data[0].get("entryCount", 0)
            unpacked_size = pack_data[0].get("unpackedSize", 0)
            print(f"\n[📦 NPM Package Stats]: {files_count} files included, Unpacked Size: ~{round(unpacked_size / 1024, 1)} KB")
    except:
        pass

    # 8. 发布执行或指引
    print("\n" + "=" * 62)
    print(f"  [✓] Release Preparation for v{target_version} Completed!")
    print("==============================================================")

    if args.publish:
        print("\n[🚀 Triggering NPM Publish...]")
        run_command("npm publish --access public", base_dir, f"Publishing v{target_version} to NPM Registry")
        print(f"\n🎉 Successfully published knowme-careerforge-skill@v{target_version} to NPM!")
    else:
        print("\nNext steps to publish your package to NPM:")
        print(f"  1. Review packaged assets and git status.")
        print(f"  2. Run: npm publish --access public\n")
        print(f"  3. Verify with:")
        print(f"     npx knowme-careerforge-skill@{target_version} list\n")

if __name__ == "__main__":
    main()
