#!/usr/bin/env python3
"""
KnowMe CareerForge — Heuristic Token Auto-Healing Unit & Integration Tests
验证 validate-resume.py --auto-heal 阶梯算法 (Section Spacing -> Item/Bullet Spacing -> Typography Scale -> Advisory)
确保 +5px ~ +40px 物理溢出场景下单次运行 100% 自动收敛，物理字号不低于 8.8pt 安全底线。
"""

import os, sys, json, unittest, shutil, subprocess, re
from pathlib import Path

# Add scripts directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts" / "validation"))

from importlib.machinery import SourceFileLoader
val_mod = SourceFileLoader("validate_resume", str(BASE_DIR / "scripts" / "validation" / "validate-resume.py")).load_module()

class TestAutoHealingLadder(unittest.TestCase):
    def setUp(self):
        self.workspace_dir = BASE_DIR / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.test_html = self.workspace_dir / "test_auto_heal_tmp.html"
        
        # Load minimal template as baseline
        src_template = BASE_DIR / "src" / "templates" / "minimal" / "template.html"
        src_css = BASE_DIR / "src" / "templates" / "minimal" / "style.css"
        base_css = BASE_DIR / "src" / "templates" / "common" / "base.css"
        
        combined_css = base_css.read_text(encoding="utf-8") + "\n" + src_css.read_text(encoding="utf-8")
        html_text = src_template.read_text(encoding="utf-8")
        html_text = html_text.replace('<link rel="stylesheet" href="style.css">', f"<style>\n{combined_css}\n</style>")
        self.test_html.write_text(html_text, encoding="utf-8")

    def tearDown(self):
        if self.test_html.exists():
            self.test_html.unlink()

    def test_update_root_token(self):
        """Test that update_root_token replaces existing variables or injects into :root."""
        ok = val_mod.update_root_token(self.test_html, "--resume-space-section", "8.5pt")
        self.assertTrue(ok)
        content = self.test_html.read_text(encoding="utf-8")
        self.assertIn("--resume-space-section: 8.5pt;", content)

        # Inject brand new token
        ok2 = val_mod.update_root_token(self.test_html, "--new-test-token", "42px")
        self.assertTrue(ok2)
        content2 = self.test_html.read_text(encoding="utf-8")
        self.assertIn("--new-test-token: 42px;", content2)

    def test_auto_heal_no_overflow_noop(self):
        """If document is already within A4 (<= 1122.5px), no healing needed."""
        res = val_mod.auto_heal_resume(self.test_html, max_pages=1)
        self.assertTrue(res["healed"])
        self.assertEqual(res["iterations"], 0)
        self.assertEqual(res["stage"], "none")

    def test_auto_heal_convergence_under_overflow(self):
        """
        Simulate an overflow of ~25px to ~40px by inflating spacing tokens,
        verify that auto_heal_resume converges within the ladder.
        """
        # Artificially expand spacing
        val_mod.update_root_token(self.test_html, "--resume-space-section", "22pt")
        val_mod.update_root_token(self.test_html, "--resume-space-item", "16pt")
        val_mod.update_root_token(self.test_html, "--resume-space-bullet", "5pt")

        res = val_mod.auto_heal_resume(self.test_html, max_pages=1)
        self.assertTrue(res["healed"], "Auto-healing must successfully converge")
        self.assertLessEqual(res["finalHeight"], 1124.5, "Final height must fit within A4 standard height")
        self.assertIn(res["stage"], ["section_spacing", "item_bullet_spacing", "typography", "none"])

    def test_typography_lower_bound_safety(self):
        """Verify that body font size never drops below the 8.8pt physical readability invariant."""
        # Force huge content that exhausts stages
        val_mod.update_root_token(self.test_html, "--resume-space-section", "25pt")
        val_mod.update_root_token(self.test_html, "--resume-space-item", "18pt")

        res = val_mod.auto_heal_resume(self.test_html, max_pages=1)
        content = self.test_html.read_text(encoding="utf-8")
        
        # Extract font size if tuned
        m = re.search(r'--resume-font-size-body\s*:\s*([\d\.]+)pt', content)
        if m:
            font_size = float(m.group(1))
            self.assertGreaterEqual(font_size, 8.8, "Body font size must never drop below 8.8pt safe limit")

    def test_stage_4_content_condense_advisory(self):
        """When content is massively overflowing (+200px), generate targeted advisory with selectors and char estimates."""
        advisory = val_mod.generate_content_condense_advisory(self.test_html, delta_px=150.0)
        self.assertIn("overflowDeltaPx", advisory)
        self.assertIn("estimatedExcessLines", advisory)
        self.assertIn("estimatedExcessChars", advisory)
        self.assertIn("targetNodes", advisory)
        self.assertIn("guidance", advisory)
        self.assertGreater(advisory["estimatedExcessChars"], 50)
        self.assertGreater(len(advisory["targetNodes"]), 0)

    def test_cli_auto_heal_flag(self):
        """Test validate-resume.py CLI with --auto-heal and --json."""
        cmd = [
            sys.executable, str(BASE_DIR / "scripts" / "validation" / "validate-resume.py"),
            "--html", str(self.test_html),
            "--auto-heal",
            "--json"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
        self.assertEqual(proc.returncode, 0, f"validate-resume.py CLI failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertIn("auto_heal", data["checks"])
        self.assertTrue(data["checks"]["auto_heal"]["healed"])

if __name__ == "__main__":
    unittest.main()
