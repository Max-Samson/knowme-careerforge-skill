#!/usr/bin/env python3
"""
KnowMe CareerForge — Workflows, Role Knowledge & Reasoning Test Suite
验证 6 大工作流定义、9 种岗位画像数据完整性、JD 分析引擎与搜索排序引擎。
"""

import os, sys, json, unittest, subprocess
from pathlib import Path

class TestWorkflowsAndKnowledge(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.workflows_dir = self.base_dir / "src" / "workflows"
        self.roles_dir = self.base_dir / "src" / "knowledge" / "roles"
        self.references_dir = self.base_dir / "src" / "references"
        self.scripts_dir = self.base_dir / "scripts"

    def test_all_workflow_documents_exist(self):
        expected_docs = [
            "AGENT.md",
            "ARCHITECTURE.md",
            "SKILL.md",
            "CLAUDE.md"
        ]
        for doc in expected_docs:
            with self.subTest(document=doc):
                doc_path = self.base_dir / doc
                self.assertTrue(doc_path.exists(), f"Core spec document '{doc}' must exist in project root")
                self.assertGreater(len(doc_path.read_text(encoding="utf-8")), 100, f"Document '{doc}' must not be empty")

    def test_all_reference_documents_exist(self):
        expected_references = [
            "01-evidence-mining.md",
            "02-career-goal.md",
            "03-jd-analysis.md",
            "04-template-selection.md",
            "05-html-canvas-tokens.md",
            "06-qa-and-rendering.md"
        ]
        for ref in expected_references:
            with self.subTest(reference=ref):
                ref_path = self.references_dir / ref
                self.assertTrue(ref_path.exists(), f"Reference manual '{ref}' must exist in src/references/")
                self.assertGreater(len(ref_path.read_text(encoding="utf-8")), 100, f"Reference '{ref}' must not be empty")
    def test_role_profiles_integrity(self):
        expected_roles = [
            "ai-agent-engineer.json",
            "frontend.json",
            "java-backend.json",
            "node-fullstack.json",
            "architect.json",
            "product-manager.json",
            "cpp-systems.json",
            "ios-engineer.json",
            "android-engineer.json"
        ]
        required_fields = ["id", "name", "category", "mustHaveSkills", "niceToHaveSkills", "evidenceSignals", "keywords"]

        for rf in expected_roles:
            with self.subTest(role=rf):
                rf_path = self.roles_dir / rf
                self.assertTrue(rf_path.exists(), f"Role profile '{rf}' must exist in src/knowledge/roles/")
                data = json.loads(rf_path.read_text(encoding="utf-8"))
                for field in required_fields:
                    self.assertIn(field, data, f"Role profile '{rf}' missing required field: {field}")
                    self.assertGreater(len(data[field]), 0, f"Role field '{field}' in '{rf}' must not be empty")

    def test_jd_analyzer_accuracy(self):
        sample_jd = """
        职位：资深大模型算法与 Agent 架构师
        职责：负责 LangGraph 多智能体协同系统设计，优化 RAG 向量召回管线与 Prompt 调优。
        要求：精通 Python、FastAPI、Qdrant、Docker，熟悉 Kubernetes。
        """
        cmd = [sys.executable, str(self.scripts_dir / "evidence" / "analyze-jd.py"), "--text", sample_jd, "--json"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
        self.assertEqual(proc.returncode, 0, f"analyze-jd.py failed: {proc.stderr}")

        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["category"], "engineering-ai")
        self.assertIn("Python", result["detectedSkills"])
        self.assertIn("FastAPI", result["detectedSkills"])
        self.assertIn("RAG", result["detectedSkills"])

    def test_template_search_ranking_relevance(self):
        # 针对 AI Agent 角色检索
        cmd_ai = [sys.executable, str(self.scripts_dir / "template" / "search-template.py"), "AI Agent Engineer", "--json"]
        proc_ai = subprocess.run(cmd_ai, capture_output=True, text=True, cwd=str(self.base_dir))
        results_ai = json.loads(proc_ai.stdout)
        self.assertGreater(len(results_ai), 0)
        top_id = results_ai[0].get("id") or results_ai[0].get("template", {}).get("id")
        self.assertIn(top_id, ["modern", "minimal", "classic"])

        # 针对高管/总监角色检索
        cmd_exec = [sys.executable, str(self.scripts_dir / "template" / "search-template.py"), "技术总监 CTO", "--json"]
        proc_exec = subprocess.run(cmd_exec, capture_output=True, text=True, cwd=str(self.base_dir))
        results_exec = json.loads(proc_exec.stdout)
        top_exec_id = results_exec[0].get("id") or results_exec[0].get("template", {}).get("id")
        self.assertEqual(top_exec_id, "executive", "Executive template must rank #1 for Director/CTO roles")
if __name__ == "__main__":
    unittest.main()
