#!/usr/bin/env python3
"""
KnowMe CareerForge — Codebase & Git Evidence Miner (repo-to-resume-tailor engine)
深度解析本地代码工程、依赖清单、系统架构与 Git 提交历史，提取 L1~L3 结构化证据链并输出 Candidate Master Profile。
"""

import sys, os, json, argparse, re, subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()

TECH_SIGNATURES = {
    # AI / LLM & Agents
    "LangChain": ["langchain", "langchain-core", "@langchain/core"],
    "LangGraph": ["langgraph", "@langchain/langgraph"],
    "LlamaIndex": ["llama-index", "llamaindex"],
    "Qdrant": ["qdrant-client", "@qdrant/js-client-rest"],
    "Milvus": ["pymilvus", "@zilliz/milvus2-sdk-node"],
    "FastAPI": ["fastapi", "uvicorn"],
    "PyTorch": ["torch", "torchvision"],
    "OpenAI SDK": ["openai", "@openai/openai"],
    # Web & Fullstack
    "TypeScript": ["typescript", "ts-node", "@types/node"],
    "React": ["react", "react-dom", "next"],
    "Next.js": ["next"],
    "Vue.js": ["vue", "nuxt"],
    "Node.js": ["express", "koa", "nestjs", "@nestjs/core", "fastify"],
    "Tailwind CSS": ["tailwindcss", "@tailwindcss/postcss"],
    "Playwright": ["playwright", "@playwright/test"],
    "GraphQL": ["graphql", "apollo-server", "@apollo/client"],
    # Backend & Systems
    "Go / Golang": ["github.com/gin-gonic/gin", "google.golang.org/grpc"],
    "Rust": ["tokio", "serde", "actix-web", "axum"],
    "Spring Boot": ["spring-boot", "org.springframework.boot"],
    # Database & Cache
    "PostgreSQL": ["pg", "psycopg2", "asyncpg", "typeorm", "prisma"],
    "MySQL": ["mysql", "mysql2", "pymysql"],
    "Redis": ["redis", "ioredis", "aioredis"],
    "Elasticsearch": ["elasticsearch", "@elastic/elasticsearch"],
    # DevOps & Infrastructure
    "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "Kubernetes": ["k8s", "helm", "Deployment", "StatefulSet"],
    "GitHub Actions": [".github/workflows"]
}

def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> str:
    try:
        res = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        return res.stdout.strip() if res.returncode == 0 else ""
    except Exception:
        return ""

def scan_repo(repo_path: Path) -> Dict[str, Any]:
    repo_path = repo_path.resolve()
    facts: Dict[str, Any] = {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "detected_languages": {},
        "detected_tech_stacks": set(),
        "architectural_signals": [],
        "author_info": {},
        "git_stats": {},
        "key_dependencies": [],
        "evidence_items": []
    }

    if not repo_path.exists() or not repo_path.is_dir():
        return facts

    # 1. Git 信息提取 (Author, commits, tags)
    git_dir = repo_path / ".git"
    if git_dir.exists():
        user_name = run_cmd(["git", "config", "user.name"], cwd=repo_path)
        user_email = run_cmd(["git", "config", "user.email"], cwd=repo_path)
        commit_count = run_cmd(["git", "rev-list", "--count", "HEAD"], cwd=repo_path)
        remote_url = run_cmd(["git", "config", "--get", "remote.origin.url"], cwd=repo_path)
        recent_commits = run_cmd(["git", "log", "-n", "8", "--pretty=format:%s"], cwd=repo_path)

        facts["author_info"]["name"] = user_name or ""
        facts["author_info"]["email"] = user_email or ""
        facts["author_info"]["git_remote"] = remote_url or ""
        facts["git_stats"]["total_commits"] = int(commit_count) if commit_count.isdigit() else 0
        facts["git_stats"]["recent_commits"] = [c for c in recent_commits.splitlines() if c]

    # 2. 统计文件类型分布
    lang_map = {
        ".ts": "TypeScript", ".tsx": "TypeScript/React", ".js": "JavaScript", ".jsx": "JavaScript/React",
        ".py": "Python", ".go": "Go", ".rs": "Rust", ".java": "Java", ".cpp": "C++", ".c": "C",
        ".html": "HTML", ".css": "CSS", ".vue": "Vue", ".sql": "SQL", ".sh": "Shell"
    }
    
    file_counts = {}
    ignored_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", ".turbo"}
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".")]
        for f in files:
            p = Path(root) / f
            ext = p.suffix.lower()
            if ext in lang_map:
                lang = lang_map[ext]
                file_counts[lang] = file_counts.get(lang, 0) + 1

    facts["detected_languages"] = file_counts

    # 3. 依赖文件深度解析
    dep_names = set()
    
    # 3.1 Node/TS
    pkg_json = repo_path / "package.json"
    if pkg_json.exists():
        try:
            pkg_data = json.loads(pkg_json.read_text(encoding="utf-8"))
            if not facts["author_info"].get("name") and pkg_data.get("author"):
                author_val = pkg_data.get("author")
                facts["author_info"]["name"] = author_val if isinstance(author_val, str) else author_val.get("name", "")
            if not facts["author_info"].get("git_remote") and pkg_data.get("repository"):
                repo_val = pkg_data.get("repository")
                facts["author_info"]["git_remote"] = repo_val if isinstance(repo_val, str) else repo_val.get("url", "")
            
            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
            dep_names.update(deps.keys())
        except Exception:
            pass

    # 3.2 Python
    req_txt = repo_path / "requirements.txt"
    if req_txt.exists():
        try:
            for line in req_txt.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    dep_names.add(re.split(r'[=<>~]', line)[0].strip().lower())
        except Exception:
            pass

    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8").lower()
            for key in ["fastapi", "torch", "langchain", "qdrant", "pytest", "pydantic"]:
                if key in content:
                    dep_names.add(key)
        except Exception:
            pass

    # 3.3 Go
    gomod = repo_path / "go.mod"
    if gomod.exists():
        try:
            for line in gomod.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("require") or " " in line:
                    parts = line.split()
                    if len(parts) >= 2 and "/" in parts[0]:
                        dep_names.add(parts[0])
        except Exception:
            pass

    # 3.4 Rust
    cargo = repo_path / "Cargo.toml"
    if cargo.exists():
        try:
            for line in cargo.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("["):
                    dep_names.add(line.split("=")[0].strip().lower())
        except Exception:
            pass

    # 4. 匹配技术栈标签
    for tech, sigs in TECH_SIGNATURES.items():
        for sig in sigs:
            if sig.lower() in [d.lower() for d in dep_names] or (repo_path / sig).exists():
                facts["detected_tech_stacks"].add(tech)
                break

    # 5. 架构与工程化信号
    if (repo_path / "packages").exists() or (repo_path / "pnpm-workspace.yaml").exists():
        facts["architectural_signals"].append("Monorepo 模块化架构")
    if (repo_path / "Dockerfile").exists() or (repo_path / "docker-compose.yml").exists():
        facts["architectural_signals"].append("Docker 容器化交付")
    if (repo_path / ".github" / "workflows").exists():
        facts["architectural_signals"].append("CI/CD 自动化流水线")
    if (repo_path / "tests").exists() or (repo_path / "test").exists():
        facts["architectural_signals"].append("自动化单元/集成测试")

    facts["key_dependencies"] = sorted(list(dep_names))
    facts["detected_tech_stacks"] = sorted(list(facts["detected_tech_stacks"]))

    # 6. 生成 L1~L3 证据项
    evidence_items = []
    if facts["detected_tech_stacks"]:
        evidence_items.append({
            "claim": f"基于 {', '.join(facts['detected_tech_stacks'][:4])} 构建核心工程架构，实现高可靠端到端业务流",
            "evidenceLevel": "L1",
            "evidenceSource": f"代码库依赖配置文件 ({', '.join([f for f in ['package.json', 'go.mod', 'requirements.txt', 'Cargo.toml'] if (repo_path / f).exists()]) or '依赖树'})",
            "keywords": facts["detected_tech_stacks"][:5]
        })

    if facts["architectural_signals"]:
        evidence_items.append({
            "claim": f"主导设计工程架构体系，落地 {', '.join(facts['architectural_signals'])}，保障交付效率与质量",
            "evidenceLevel": "L1",
            "evidenceSource": "工程根目录架构配置文件与流水线定义",
            "keywords": ["Architecture", "CI/CD", "Testing", "DevOps"]
        })

    if facts["git_stats"].get("total_commits", 0) > 10:
        evidence_items.append({
            "claim": f"持续推进工程重构与版本迭代，累计提交 {facts['git_stats']['total_commits']} 次代码并完成多版本发布",
            "evidenceLevel": "L2",
            "evidenceSource": "Git 提交历史与版本变更记录",
            "keywords": ["Refactoring", "Git", "Release Engineering"]
        })

    facts["evidence_items"] = evidence_items
    return facts

def build_master_profile(facts: Dict[str, Any], user_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    overrides = user_overrides or {}
    author = facts.get("author_info", {})
    
    name = overrides.get("name") or author.get("name") or "求职者"
    title = overrides.get("title") or "资深工程师 / 技术专家"
    email = overrides.get("email") or author.get("email") or "candidate@example.com"
    phone = overrides.get("phone") or "138-0000-0000"
    github = overrides.get("github") or author.get("git_remote") or "https://github.com"
    
    tech_stacks = facts.get("detected_tech_stacks", [])
    languages = list(facts.get("detected_languages", {}).keys())

    profile = {
        "basics": {
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "location": overrides.get("location") or "北京 / 远程",
            "github": github,
            "summary": f"拥有坚实的技术研发与工程化落地实战经验，主导过多个基于 {', '.join((tech_stacks + languages)[:3])} 的核心系统设计与交付。"
        },
        "skills": [
            {
                "category": "核心技术栈",
                "items": tech_stacks if tech_stacks else ["Python", "TypeScript", "FastAPI", "React", "Docker"],
                "highlighted": tech_stacks[:4]
            },
            {
                "category": "工程化与架构",
                "items": facts.get("architectural_signals", ["CI/CD", "微服务架构", "自动化测试", "性能优化"]),
                "highlighted": ["CI/CD", "性能优化"]
            }
        ],
        "experience": [
            {
                "company": overrides.get("company") or "创新科技企业",
                "role": title,
                "startDate": "2022.06",
                "endDate": "至今",
                "location": "北京",
                "summary": "负责核心产品研发与关键架构攻坚",
                "bullets": [
                    {
                        "text": item["claim"],
                        "evidenceLevel": item["evidenceLevel"],
                        "evidenceSource": item["evidenceSource"],
                        "keywords": item["keywords"]
                    }
                    for item in facts.get("evidence_items", [])
                ]
            }
        ],
        "projects": [
            {
                "name": facts.get("repo_name", "CoreSystem"),
                "role": "核心负责人 / 主力开发者",
                "techStack": tech_stacks[:5],
                "repoUrl": github,
                "startDate": "2023.01",
                "endDate": "至今",
                "bullets": [
                    {
                        "text": item["claim"],
                        "evidenceLevel": item["evidenceLevel"],
                        "evidenceSource": item["evidenceSource"]
                    }
                    for item in facts.get("evidence_items", [])
                ]
            }
        ],
        "education": [
            {
                "institution": overrides.get("school") or "重点大学",
                "degree": overrides.get("degree") or "计算机科学与技术 本科",
                "startDate": "2016.09",
                "endDate": "2020.06"
            }
        ]
    }
    return profile

def main():
    parser = argparse.ArgumentParser(description="KnowMe CareerForge — Codebase Evidence Miner")
    parser.add_argument("--repo", "-r", default=".", help="Target repository directory (default: current directory)")
    parser.add_argument("--output", "-o", default="workspace/evidence-master.json", help="Output evidence JSON path")
    parser.add_argument("--name", help="Candidate full name override")
    parser.add_argument("--role", help="Candidate target role/title override")
    parser.add_argument("--email", help="Candidate email override")
    parser.add_argument("--phone", help="Candidate phone override")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet execution mode")

    args = parser.parse_args()
    repo_path = Path(args.repo)

    facts = scan_repo(repo_path)
    
    overrides = {}
    if args.name: overrides["name"] = args.name
    if args.role: overrides["title"] = args.role
    if args.email: overrides["email"] = args.email
    if args.phone: overrides["phone"] = args.phone

    profile = build_master_profile(facts, overrides)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        print("==============================================================")
        print("  KnowMe CareerForge — Codebase Evidence Mining Report")
        print(f"  Target Repository : {facts['repo_path']}")
        print(f"  Detected Techs    : {', '.join(facts['detected_tech_stacks']) or 'None'}")
        print(f"  Architecture      : {', '.join(facts['architectural_signals']) or 'Standard'}")
        print(f"  Evidence Generated: {len(facts['evidence_items'])} L1/L2 items")
        print(f"  Profile Written To: {out_path}")
        print("==============================================================")

if __name__ == "__main__":
    main()
