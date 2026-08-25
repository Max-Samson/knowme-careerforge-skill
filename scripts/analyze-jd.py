#!/usr/bin/env python3
"""
KnowMe CareerForge — JD Analyzer & Hiring Signal Extractor
结构化解析招聘 JD 文本，提取岗位分类、职级、必备技能、加分项与核心业务关键词。
"""

import sys, os, json, argparse, re
from pathlib import Path

COMMON_TECH_STACKS = [
    "Python", "TypeScript", "JavaScript", "Java", "Go", "Golang", "C++", "Rust",
    "React", "Vue", "Next.js", "Node.js", "FastAPI", "Spring Boot", "NestJS",
    "LLM", "RAG", "LangGraph", "LangChain", "LlamaIndex", "VectorDB", "Qdrant",
    "Milvus", "Pinecone", "Prompt Engineering", "Prompt", "Fine-tuning", "Evaluation",
    "PostgreSQL", "MySQL", "Redis", "Kafka", "RocketMQ", "Elasticsearch",
    "Docker", "Kubernetes", "K8s", "CI/CD", "AWS", "Aliyun", "Linux"
]

def analyze_jd_text(jd_text: str) -> dict:
    text_lower = jd_text.lower()
    
    # 1. 识别岗位与职级
    seniority = "mid"
    if any(k in jd_text for k in ["资深", "专家", "架构师", "总监", "Lead", "Senior", "Principal"]):
        seniority = "senior/lead"
    elif any(k in jd_text for k in ["初级", "实习", "应届", "Junior"]):
        seniority = "junior"

    category = "engineering-ai"
    if any(k in jd_text for k in ["产品经理", "Product Manager", "总监", "Director", "业务负责人"]):
        category = "management-product"

    # 2. 匹配技术栈与关键词
    detected_skills = []
    for skill in COMMON_TECH_STACKS:
        pattern = re.compile(rf'(?:^|[^\w]){re.escape(skill)}(?:[^\w]|$)', re.IGNORECASE)
        if pattern.search(jd_text):
            detected_skills.append(skill)

    # 3. 区分必备与加分
    must_haves = detected_skills[:6] if len(detected_skills) >= 6 else detected_skills
    nice_to_haves = detected_skills[6:] if len(detected_skills) > 6 else []

    # 4. 业务痛点与职责关键词提取
    responsibilities = []
    for line in jd_text.splitlines():
        line_clean = line.strip()
        if len(line_clean) > 6 and any(verb in line_clean for verb in ["负责", "主导", "推进", "设计", "参与", "优化", "统筹", "熟练", "精通"]):
            responsibilities.append(line_clean)

    return {
        "status": "success",
        "category": category,
        "estimatedSeniority": seniority,
        "mustHaveSkills": must_haves,
        "niceToHaveSkills": nice_to_haves,
        "detectedSkills": detected_skills,
        "keyResponsibilities": responsibilities[:6],
        "hiringSignals": [
            "强调工程化与系统高并发稳定性" if "稳定" in jd_text or "高并发" in jd_text else "强调快速交付与 0-1 探索",
            "大模型与 AI Agent 场景深度落地" if "大模型" in jd_text or "rag" in text_lower or "agent" in text_lower else "传统业务系统演进"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — JD Analyzer")
    parser.add_argument("--jd", "-j", help="Path to JD text file")
    parser.add_argument("--text", "-t", help="Raw JD text string")
    parser.add_argument("--json", action="store_true", help="Output only clean JSON")

    args = parser.parse_args()

    content = ""
    if args.jd and Path(args.jd).exists():
        content = Path(args.jd).read_text(encoding="utf-8")
    elif args.text:
        content = args.text

    if not content.strip():
        # 默认样例
        content = """职位：资深 AI Agent 研发工程师
岗位职责：
1. 负责企业级多 Agent 智能协同工作流平台的设计与核心研发；
2. 主导基于 RAG 的专业知识库检索管线优化与模型微调；
3. 持续优化 Prompt 与上下文窗口，压榨模型推理延迟与 Token 成本。
任职要求：
1. 本科及以上学历，精通 Python、FastAPI 及多线程异步编程；
2. 熟练掌握 LangGraph、LangChain、LlamaIndex 等 Agent 开发框架；
3. 深入理解向量数据库（Qdrant / Milvus）原理，具备高并发高可用调优经验；
4. 熟悉 Docker、Kubernetes 云原生技术栈者优先。"""

    result = analyze_jd_text(content)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=" * 70)
    print("  KnowMe CareerForge — JD Analysis Result")
    print(f"  Category            : {result['category']}")
    print(f"  Seniority Level     : {result['estimatedSeniority']}")
    print(f"  Must-Have Skills    : {', '.join(result['mustHaveSkills'])}")
    print(f"  Nice-To-Have Skills : {', '.join(result['niceToHaveSkills'])}")
    print(f"  Hiring Signals      : {', '.join(result['hiringSignals'])}")
    print("=" * 70)

if __name__ == "__main__":
    main()
