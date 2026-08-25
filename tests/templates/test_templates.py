#!/usr/bin/env python3
"""
KnowMe CareerForge — Template Bundle Contract & Token Integrity Tests
验证 src/templates/ 下所有模板包遵循完整规范：包含 template.html, style.css, metadata.json, README.md，
验证所有声明的 customizableTokens 在 style.css 中真实定义，并验证物理 A4 印刷约束。
"""

import os, sys, json, unittest, re
from pathlib import Path

class TestTemplateContracts(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.templates_dir = self.base_dir / "src" / "templates"
        self.contract_file = self.templates_dir / "common" / "resume-contract.md"

    def test_universal_contract_exists(self):
        self.assertTrue(self.contract_file.exists(), "src/templates/common/resume-contract.md must exist")
        self.assertGreater(len(self.contract_file.read_text(encoding="utf-8")), 200)

    def test_templates_exist(self):
        self.assertTrue(self.templates_dir.exists(), "src/templates directory must exist")
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        self.assertGreaterEqual(len(template_dirs), 4, "Must have at least 4 baseline templates")

    def test_template_bundle_structure(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        required_files = ["template.html", "style.css", "metadata.json", "README.md"]
        
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                for f in required_files:
                    f_path = t_dir / f
                    self.assertTrue(f_path.exists(), f"Template '{t_dir.name}' missing {f}")
                    self.assertGreater(len(f_path.read_text(encoding="utf-8")), 10, f"{f} in '{t_dir.name}' is empty")

    def test_metadata_json_schema(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        required_keys = ["id", "name", "version", "style", "roleCategory", "layout", "visualStyle", "atsScoreTier", "supportedRoles"]
        
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                meta_path = t_dir / "metadata.json"
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                for k in required_keys:
                    self.assertIn(k, data, f"metadata.json in '{t_dir.name}' missing key: {k}")

    def test_html_contains_resume_page(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                html_path = t_dir / "template.html"
                content = html_path.read_text(encoding="utf-8")
                self.assertIn("resume-page", content, f"template.html in '{t_dir.name}' must contain .resume-page")
                self.assertIn("candidate-name", content, f"template.html in '{t_dir.name}' must contain .candidate-name")

    def test_css_contains_a4_print_geometry(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                css_path = t_dir / "style.css"
                content_clean = css_path.read_text(encoding="utf-8").replace(" ", "").replace("\t", "")
                self.assertIn("--resume-page-width:210mm", content_clean, f"style.css in '{t_dir.name}' must define 210mm width")
                self.assertIn("--resume-page-min-height:297mm", content_clean, f"style.css in '{t_dir.name}' must define 297mm min-height")
                self.assertIn("@page", content_clean, f"style.css in '{t_dir.name}' must contain @page print rule")

    def test_customizable_tokens_exist_in_css(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                meta_path = t_dir / "metadata.json"
                css_path = t_dir / "style.css"
                
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                css_content = css_path.read_text(encoding="utf-8")
                
                customizable = meta.get("customizableTokens", [])
                for token in customizable:
                    self.assertIn(token, css_content, f"Token '{token}' declared in metadata.json but missing in style.css of '{t_dir.name}'")

if __name__ == "__main__":
    unittest.main()
