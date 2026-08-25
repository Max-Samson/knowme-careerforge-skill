#!/usr/bin/env python3
"""
KnowMe CareerForge — ATS Compliance & Text Flow Test Suite
验证所有模板在 ATS 系统中的文本可提取性、标头词典合规性与联系信息解析度。
"""

import os, sys, json, unittest, re
from pathlib import Path

class TestAtsCompliance(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.templates_dir = self.base_dir / "src" / "templates"
        self.ats_rules_file = self.base_dir / "src" / "knowledge" / "ats-rules.json"

    def test_ats_rules_json_exists(self):
        self.assertTrue(self.ats_rules_file.exists(), "ats-rules.json must exist in src/knowledge/")
        rules = json.loads(self.ats_rules_file.read_text(encoding="utf-8"))
        self.assertIn("atsStandards", rules)
        self.assertIn("standardSectionHeadings", rules["atsStandards"])

    def test_candidate_name_in_all_templates(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                html_path = t_dir / "template.html"
                content = html_path.read_text(encoding="utf-8")
                self.assertTrue(
                    "candidate-name" in content or "<h1>" in content or "<h1 " in content,
                    f"Template '{t_dir.name}' must contain a candidate name node (.candidate-name or h1)"
                )

    def test_contact_information_extractability(self):
        email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        phone_pattern = re.compile(r'(?:(?:\+|00)86)?1[3-9]\d{9}|(?:1[3-9]\d-\d{4}-\d{4})')

        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                html_path = t_dir / "template.html"
                content = html_path.read_text(encoding="utf-8")
                
                # 剔除 HTML 标签取纯文本
                pure_text = re.sub(r'<[^>]+>', ' ', content)

                email_match = email_pattern.search(pure_text)
                self.assertIsNotNone(email_match, f"Template '{t_dir.name}' must contain extractable email in text stream")

                phone_match = phone_pattern.search(pure_text)
                self.assertIsNotNone(phone_match, f"Template '{t_dir.name}' must contain extractable phone in text stream")

    def test_standard_headings_presence(self):
        rules = json.loads(self.ats_rules_file.read_text(encoding="utf-8"))
        std_headings = rules["atsStandards"]["standardSectionHeadings"]
        
        flat_headings = []
        for cat, h_list in std_headings.items():
            flat_headings.extend([h.lower().replace(" ", "") for h in h_list])

        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                html_path = t_dir / "template.html"
                content = html_path.read_text(encoding="utf-8")
                
                # 提取所有标题标签文本
                headings_found = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', content, flags=re.DOTALL)
                headings_text = [re.sub(r'<[^>]+>', '', h).strip().lower().replace(" ", "") for h in headings_found]

                matched = any(any(std in h for std in flat_headings) for h in headings_text)
                self.assertTrue(matched, f"Template '{t_dir.name}' must contain standard ATS section headings")

    def test_no_forbidden_hidden_text_patterns(self):
        template_dirs = [d for d in self.templates_dir.iterdir() if d.is_dir() and d.name != "common"]
        for t_dir in template_dirs:
            with self.subTest(template=t_dir.name):
                css_path = t_dir / "style.css"
                css_content = css_path.read_text(encoding="utf-8")

                # 检查是否存在恶意隐藏文字 class
                self.assertNotIn("opacity: 0", css_content, f"Template '{t_dir.name}' should not contain opacity: 0 text masks")
                self.assertNotIn("font-size: 0", css_content, f"Template '{t_dir.name}' should not contain zero font-size text masks")

if __name__ == "__main__":
    unittest.main()
