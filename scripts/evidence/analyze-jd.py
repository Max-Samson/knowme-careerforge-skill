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
    seniority = "mid"
    if any(k in jd_text for k in ["资深", "专家", "架构师", "总监", "Lead", "Senior", "Principal"]):
        seniority = "senior/lead"
    elif any(k in jd_text for k in ["初级", "实习", "应届", "Junior"]):
        seniority = "junior"

    category = "engineering-ai"
    if any(k in jd_text for k in ["产品经理", "Product Manager", "总监", "Director", "业务负责人"]):
        category = "management-product"

    detected_skills = []
    for skill in COMMON_TECH_STACKS:
        pattern = re.compile(rf'(?:^|[^\w]){re.escape(skill)}(?:[^\w]|$)', re.IGNORECASE)
        if pattern.search(jd_text):
            detected_skills.append(skill)

    must_haves = detected_skills[:6] if len(detected_skills) >= 6 else detected_skills
    nice_to_haves = detected_skills[6:] if len(detected_skills) > 6 else []

    responsibilities = []
    for line in jd_text.splitlines():
        line_clean = line.strip()
        if len(line_clean) > 6 and any(verb in line_clean for verb in ["负责", "主导", "推进", "设计", "参与", "优化", "统筹", "熟练", "精通"]):
            responsibilities.append(line_clean)

    return {
        "status": "success",
        "seniority": seniority,
        "category": category,
        "detectedSkills": detected_skills,
        "mustHaveSkills": must_haves,
        "niceToHaveSkills": nice_to_haves,
        "keyResponsibilities": responsibilities[:5]
    }

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — JD Analyzer")
    parser.add_argument("--jd", help="Path to JD markdown/text file")
    parser.add_argument("--text", help="Raw JD text string")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()
    jd_content = ""

    if args.jd:
        p = Path(args.jd)
        if not p.exists():
            print(f"Error: JD file not found: {p}", file=sys.stderr)
            sys.exit(1)
        jd_content = p.read_text(encoding="utf-8")
    elif args.text:
        jd_content = args.text
    else:
        if not sys.stdin.isatty():
            jd_content = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    result = analyze_jd_text(jd_content)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("  KnowMe CareerForge — JD Analysis Report")
        print("=" * 70)
        print(f"  Target Category   : {result['category']}")
        print(f"  Seniority Level   : {result['seniority']}")
        print(f"  Must-have Skills  : {', '.join(result['mustHaveSkills']) or 'None'}")
        print(f"  Nice-to-have Skills: {', '.join(result['niceToHaveSkills']) or 'None'}")
        print("  Key Responsibilities:")
        for r in result["keyResponsibilities"]:
            print(f"    • {r}")
        print("=" * 70)

if __name__ == "__main__":
    main()
