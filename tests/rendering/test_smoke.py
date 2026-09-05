#!/usr/bin/env python3
"""
KnowMe CareerForge — End-to-End Smoke & Functional Pipeline Tests
验证完整功能链路：
1. 模板检索引擎打分与 JSON 返回 (scripts/template/search-template.py)
2. 所有 4 款模板的实例化与关键词高亮注入 (scripts/template/instantiate-resume.py)
3. 布局与 ATS 规则自动化验证 (scripts/validation/validate-resume.py)
4. 知识库编译器 (scripts/build/build-knowledge.py) 执行
5. 可视化模板画廊生成器 (scripts/build/build-gallery.py) 执行
6. 事实证据挖掘器 (scripts/evidence/extract-evidence.py) 执行
7. 一键全流程管线 (scripts/pipeline/forge.py) 执行
8. 规范文档 (scripts/Agent.md) 完整性验证
"""

import os, sys, json, unittest, subprocess
from pathlib import Path

class TestSmokePipeline(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.workspace_dir = self.base_dir / "workspace"
        self.output_dir = self.base_dir / "output"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def test_1_search_template_cli(self):
        cmd = [sys.executable, str(self.scripts_dir / "template" / "search-template.py"), "Senior Backend Engineer", "--json"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"search-template.py failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(len(data), 10, "Search must evaluate all 10 templates")
        self.assertIn("score", data[0])
        self.assertIn("template", data[0])

    def test_2_instantiate_and_keyword_highlighting(self):
        test_keywords = "Python,FastAPI,LangGraph,Qdrant"
        all_templates = [
            "minimal", "modern", "executive", "classic",
            "academic-research", "international-flow", "creative-tech",
            "compact-dense", "startup-generalist", "data-analyst"
        ]
        for template_id in all_templates:
            with self.subTest(template=template_id):
                target_html = self.workspace_dir / f"test_{template_id}.html"
                cmd_inst = [
                    sys.executable, str(self.scripts_dir / "template" / "instantiate-resume.py"),
                    "--template", template_id,
                    "--keywords", test_keywords,
                    "--output", str(target_html)
                ]
                proc_inst = subprocess.run(cmd_inst, capture_output=True, text=True, cwd=str(self.base_dir))
                self.assertEqual(proc_inst.returncode, 0, f"instantiate-resume failed for {template_id}: {proc_inst.stderr}")
                self.assertTrue(target_html.exists(), f"Output canvas {target_html} must exist")

                content = target_html.read_text(encoding="utf-8")
                # 验证 CSS 内联
                self.assertIn("<style>", content)
                self.assertNotIn('<link rel="stylesheet" href="style.css">', content)

                # 验证关键词高亮注入
                self.assertTrue("<strong>" in content or "tech-tags" in content)

                # 运行验证
                cmd_val = [
                    sys.executable, str(self.scripts_dir / "validation" / "validate-resume.py"),
                    "--html", str(target_html),
                    "--expected-pages", "1",
                    "--json"
                ]
                proc_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(self.base_dir))
                self.assertEqual(proc_val.returncode, 0, f"validate-resume failed for {template_id}: {proc_val.stderr}")
                val_data = json.loads(proc_val.stdout)
                self.assertEqual(val_data["status"], "PASS")

                # 清理
                if target_html.exists():
                    target_html.unlink()

    def test_3_build_knowledge_compiler(self):
        cmd = [sys.executable, str(self.scripts_dir / "build" / "build-knowledge.py")]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"build-knowledge.py failed: {proc.stderr}")

        index_file = self.base_dir / "src" / "knowledge" / "index.json"
        self.assertTrue(index_file.exists())
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        self.assertEqual(index_data["totalRoles"], 9)
        self.assertEqual(index_data["totalTemplates"], 10)

    def test_4_build_gallery_generator(self):
        cmd = [sys.executable, str(self.scripts_dir / "build" / "build-gallery.py")]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"build-gallery.py failed: {proc.stderr}")

        gallery_index = self.output_dir / "templates_gallery" / "index.html"
        self.assertTrue(gallery_index.exists())
        content = gallery_index.read_text(encoding="utf-8")
        for t in ["minimal", "modern", "executive", "classic", "academic-research", "international-flow", "creative-tech", "compact-dense", "startup-generalist", "data-analyst"]:
            self.assertIn(f"{t}.html", content)

    def test_5_extract_evidence_miner(self):
        out_json = self.workspace_dir / "test_evidence.json"
        cmd = [
            sys.executable, str(self.scripts_dir / "evidence" / "extract-evidence.py"),
            "--repo", str(self.base_dir),
            "--name", "测试自动化候选人",
            "--output", str(out_json),
            "--quiet"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"extract-evidence failed: {proc.stderr}")
        self.assertTrue(out_json.exists())
        data = json.loads(out_json.read_text(encoding="utf-8"))
        self.assertEqual(data["basics"]["name"], "测试自动化候选人")
        self.assertTrue(len(data["experience"]) > 0)
        self.assertTrue(len(data["skills"]) > 0)
        if out_json.exists():
            out_json.unlink()

    def test_6_forge_one_shot_pipeline(self):
        out_pdf = self.workspace_dir / "test_forge.pdf"
        out_html = self.workspace_dir / "test_forge.html"
        cmd = [
            sys.executable, str(self.scripts_dir / "pipeline" / "forge.py"),
            "--repo", str(self.base_dir),
            "--role", "全栈工程师",
            "--name", "张集成",
            "--template", "minimal",
            "--output", str(out_pdf),
            "--html-output", str(out_html),
            "--quiet"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"forge.py failed: {proc.stderr}")
        self.assertTrue(out_html.exists())
        self.assertTrue(out_pdf.exists())
        self.assertTrue(out_pdf.stat().st_size > 1000)
        
        if out_pdf.exists(): out_pdf.unlink()
        if out_html.exists(): out_html.unlink()

    def test_7_agent_spec_document_exists(self):
        agent_md = self.scripts_dir / "Agent.md"
        self.assertTrue(agent_md.exists(), "scripts/Agent.md must exist")
        content = agent_md.read_text(encoding="utf-8")
        self.assertIn("pipeline/", content)
        self.assertIn("evidence/", content)
        self.assertIn("template/", content)
        self.assertIn("validation/", content)
        self.assertIn("rendering/", content)
        self.assertIn("build/", content)

if __name__ == "__main__":
    unittest.main()
