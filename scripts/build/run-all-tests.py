#!/usr/bin/env python3
"""
KnowMe CareerForge — Unified Full-Chain Test Runner
执行所有自动化测试套件（Templates, ATS, Workflows, End-to-End Pipeline），输出格式化质检报告。
"""

import os, sys, unittest, time
from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

def run_all_test_suites():
    start_time = time.time()
    base_dir = get_project_root()
    tests_dir = base_dir / "tests"

    print("==============================================================")
    print("  KnowMe CareerForge — Full-Chain Automated Test Suite")
    print(f"  Test Root : {tests_dir}")
    print("==============================================================")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    elapsed = time.time() - start_time

    print("\n" + "=" * 62)
    print("  Test Execution Summary")
    print(f"  Total Tests Run : {result.testsRun}")
    print(f"  Failures        : {len(result.failures)}")
    print(f"  Errors          : {len(result.errors)}")
    print(f"  Skipped         : {len(result.skipped)}")
    print(f"  Time Elapsed    : {elapsed:.2f}s")
    print(f"  Overall Status  : {'[✓] ALL TESTS PASSED' if result.wasSuccessful() else '[✗] TEST FAILURES DETECTED'}")
    print("==============================================================")

    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_test_suites())
