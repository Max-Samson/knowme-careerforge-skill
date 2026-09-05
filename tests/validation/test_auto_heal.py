"""Run isolated real-browser regression coverage (including transactional autoheal)."""
import subprocess
import unittest
from pathlib import Path


class TestBrowserEngine(unittest.TestCase):
    def test_browser_engine_contracts(self):
        root = Path(__file__).resolve().parents[2]
        proc = subprocess.run(
            ["node", "--test", "tests/rendering/browser-engine.test.js"],
            cwd=root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
