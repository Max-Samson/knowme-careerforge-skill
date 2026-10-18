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

# ASCII identifier boundaries allow Chinese prose next to technology names.
SKILL_PATTERNS = {
    skill: re.compile(rf'(?<![A-Za-z0-9_+]){re.escape(skill)}(?![A-Za-z0-9_+])', re.IGNORECASE)
    for skill in COMMON_TECH_STACKS
}
REQUIREMENT_MARKERS = {
    'must': re.compile(r'必备(?:技能)?|必须|任职要求|岗位要求|基本要求|(?<![A-Za-z])(?:required|requirements|must[- ]have|mandatory)(?![A-Za-z])', re.I),
    'nice': re.compile(r'加分(?:项)?|优先|非必需|非必须|不要求|无需|(?<![A-Za-z])(?:nice[- ]to[- ]have|preferred|optional|not required)(?![A-Za-z])', re.I),
}


def classify_skills(jd_text, detected_skills):
    """Classify only explicit requirements; ambiguous or conflicting mentions stay unclassified."""
    evidence = {skill: set() for skill in detected_skills}
    section = None
    for line in jd_text.splitlines():
        markdown_heading = bool(re.match(r'^\s*#{1,6}\s+', line))
        line = line.strip().strip('#* ').strip()
        if not line:
            continue
        heading = line.rstrip(':：').strip()
        kinds = [kind for kind, pattern in REQUIREMENT_MARKERS.items() if pattern.fullmatch(heading)]
        if kinds:
            section = kinds[0]
            continue
        # A different heading terminates an explicit requirements section.
        if markdown_heading or (line.endswith((':', '：')) and not any(p.search(line) for p in SKILL_PATTERNS.values())):
            section = None
            continue
        local_kind = section
        for clause in re.split(r'([。；;，,!?！？]|\.(?=\s|$))', line):
            if clause in ('。', '；', ';', '.', '!', '?', '！', '？'):
                local_kind = section
                continue
            markers = {kind for kind, pattern in REQUIREMENT_MARKERS.items() if pattern.search(clause)}
            # Negated requirements must not also count as positive "required".
            if re.search(r'not required|非必须', clause, re.I):
                markers.discard('must')
            kind = next(iter(markers)) if len(markers) == 1 else local_kind if not markers else None
            local_kind = kind
            for skill in detected_skills:
                if SKILL_PATTERNS[skill].search(clause) and kind:
                    evidence[skill].add(kind)
    return ([s for s in detected_skills if evidence[s] == {'must'}],
            [s for s in detected_skills if evidence[s] == {'nice'}])


def analyze_jd_text(jd_text: str) -> dict:
    seniority = "mid"
    if any(k in jd_text for k in ["资深", "专家", "架构师", "总监", "Lead", "Senior", "Principal"]):
        seniority = "senior/lead"
    elif any(k in jd_text for k in ["初级", "实习", "应届", "Junior"]):
        seniority = "junior"

    category = "engineering-ai"
    if any(k in jd_text for k in ["产品经理", "Product Manager", "总监", "Director", "业务负责人"]):
        category = "management-product"

    detected_skills = [skill for skill, pattern in SKILL_PATTERNS.items() if pattern.search(jd_text)]
    must_haves, nice_to_haves = classify_skills(jd_text, detected_skills)

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
