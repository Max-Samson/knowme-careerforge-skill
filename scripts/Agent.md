# KnowMe CareerForge — Scripts Architecture & Agent Execution Specification

> **定位**：面向 AI Agent 与研发工程师的 `scripts/` 工具链架构规范、模块划分标准与执行契约手册。
>
> **版本**：v1.0.0-modular  
> **核心原则**：Domain-Driven Modularization · Quiet Agent Execution · Deterministic Rendering · Zero-Dependency Python Core

---

## 1. 目录架构与模块职责划分 (Domain Architecture)

为了保证脚本工具链的高内聚、低耦合与易维护性，`scripts/` 目录划分为 **6 大功能领域模块**：

```text
scripts/
├── Agent.md                         # 本规范文档 (Source of Truth for Agent/Dev)
│
├── pipeline/                        # 【模块 1: 端到端统筹管线】
│   └── forge.py                     # 一键端到端装配引擎 (One-Shot Pipeline: 挖掘 -> 装配 -> QA -> PDF)
│
├── evidence/                        # 【模块 2: 事实与证据挖掘 (repo-to-resume)】
│   ├── extract-evidence.py          # 代码仓与 Git 事实挖掘器 (提取技术栈、架构信号、Git 贡献 -> L1~L3 证据链)
│   └── analyze-jd.py                # 目标 JD 深度分析器 (提取职级、分类、必备/加分项、痛点关键词)
│
├── template/                        # 【模块 3: 模板检索与工作区装配】
│   ├── search-template.py           # 多维加权打分搜索引擎 (BM25 + 岗位/风格/页数/密度推荐)
│   └── instantiate-resume.py        # 模板装配与数据注入引擎 (CSS 内联单文件 + 结构化数据注入 + 关键词高亮)
│
├── validation/                      # 【模块 4: 双重 QA 自动化质检】
│   ├── validate-resume.py           # 语义结构、Design Tokens 与字符密度轻量校验器
│   ├── validate-layout.ts           # Playwright DOM 盒模型物理高度 (1122.5px A4) 溢出与孤行检测
│   └── validate-ats.ts              # ATS 纯文本流解析、联系方式与 H1/H2 标头层级校验
│
├── rendering/                       # 【模块 5: 确定性 PDF 渲染导出】
│   ├── render-pdf.py                # 跨平台自愈式 PDF 渲染调度器 (自动探测 Playwright 及全平台 Chromium/Edge/Brave)
│   └── render-pdf.ts                # Playwright 驱动的无损矢量 A4 PDF 渲染器
│
└── build/                           # 【模块 6: 编译构建、测试与发布工具链】
    ├── build-knowledge.py           # 岗位画像与模板知识库索引编译器 (生成 index.json & templates.json)
    ├── build-gallery.py             # 静态交互式模板画廊生成器 (编译 output/templates_gallery/)
    ├── run-all-tests.py             # 全链路自动化测试运行器 (discover & run tests/)
    ├── sync-version.py              # 多清单版本号同步器 (package.json / pyproject.toml / skill.json / cli)
    └── release.py                   # 自动化发布流水线引擎 (版本对齐 -> 编译 -> 测试 -> 打包预检)
```
---

## 2. 脚本契约与 Agent 调用规范 (Execution Contracts)

### 2.1 推荐调用模式：一键直达管线 (One-Shot Execution)

AI Agent 响应用户求职定制需求时，**强烈推荐首选一键管线**：

```bash
# 静默全流程执行 (后台自动完成：代码仓扫描 -> 模板检索 -> 工作区注入 -> Dual QA -> PDF 导出)
python3 scripts/pipeline/forge.py --repo . --role "<Target Role>" --jd "<path/to/jd.txt>" --template modern --quiet
```
* **CLI 等价形式**：`knowme forge --repo . --role "<Target Role>" --template modern --quiet`
* **返回格式**：结构化 JSON，供 Agent 直接获取交付文件路径：
  ```json
  {
    "status": "SUCCESS",
    "htmlCanvas": "workspace/resume.html",
    "pdfDelivery": "workspace/resume.pdf",
    "evidenceProfile": "workspace/evidence-master.json",
    "templateUsed": "modern"
  }
  ```

---

### 2.2 细粒度分步调用接口 (Granular Step-by-Step APIs)

当 Agent 或用户需要分步微调、审查证据或调校 Design Tokens 时，按以下顺序执行：

| 步骤 | 阶段 | 推荐命令 | 关键参数 | 产出物 |
| :--- | :--- | :--- | :--- | :--- |
| **Step 1** | **事实挖掘** | `python3 scripts/evidence/extract-evidence.py` | `--repo <dir>` `--name <name>` `--quiet` | `workspace/evidence-master.json` |
| **Step 2** | **JD 解析** | `python3 scripts/evidence/analyze-jd.py` | `--jd <file>` 或 `--text "<str>"` `--json` | 提取必须技能与权重关键词 |
| **Step 3** | **模板检索** | `python3 scripts/template/search-template.py` | `"<Role>"` `--style "<style>"` `--json` | 加权推荐模板列表 (Top 1) |
| **Step 4** | **画布装配** | `python3 scripts/template/instantiate-resume.py` | `--template <id>` `--profile <json>` `--keywords <kw>` | `workspace/resume.html` (单文件内联) |
| **Step 5** | **质检自愈** | `python3 scripts/validation/validate-resume.py` | `--html workspace/resume.html` `--expected-pages 1` | QA 诊断状态与溢出提示 |
| **Step 6** | **PDF 导出** | `python3 scripts/rendering/render-pdf.py` | `workspace/resume.html` `workspace/resume.pdf` `--quiet` | `workspace/resume.pdf` (确定性矢量) |

---

## 3. Agent 对话降噪规范 (Strict Quiet Execution Protocol)

为了杜绝对话框中出现几百行冗余代码或中间脚本，所有接入的 AI Agent 必须遵守以下铁律：

1. **禁止在 Chat 中打印原始 HTML/CSS**：禁止将 `workspace/resume.html` 的数百行代码打印到对话框中；
2. **禁止在 Chat 中编写现场临时脚本**：严禁现场生成临时验证脚本或修改场脚本，必须使用 `scripts/` 下既有的标准工具链；
3. **静默执行原则**：调用脚本时统一添加 `--quiet` 或 `--json` 参数；
4. **标准交付物格式**：
   ```markdown
   ### 🎯 职业定位与核心价值主张 (Core Value Proposition)
   > **[姓名] · [目标岗位]**
   > *[15~25字核心定位与价值阐述]*

   ---

   ### 🛡️ Top 3 真实证据链亮点 (L1/L2 级别可追溯事实)
   1. **[业务方向/核心架构]**: [动词 + 可量化成果 + 证据来源]
   2. **[核心技术栈工程化]**: [关键框架与工程规范落地]
   3. **[交付与系统效能]**: [稳定性/CI-CD/性能指标]

   ---

   ### 📄 最终交付产物
   - **PDF 终稿 (确定性 A4)**: `workspace/resume.pdf`
   - **HTML 修改场 (Design Tokens)**: `workspace/resume.html`
   - **证据事实底座**: `workspace/evidence-master.json`
   ```

---

## 4. 后续开发与扩展规范 (Developer Standards)

为保持工程整洁与跨平台稳定性，后续新增或修改脚本必须遵循以下标准：

### 4.1 根路径自适应解析 (Root Path Resolution Standard)
所有 Python 脚本**严禁使用硬编码相对路径**，必须通过自适应探测函数定位项目根目录：
```python
def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "SKILL.md").exists() or (curr / "package.json").exists():
            return curr
        curr = curr.parent
    return Path.cwd()
```

### 4.2 零重型依赖原则 (Zero-Heavy-Dependency)
* 核心运行脚本（`evidence/`、`template/`、`pipeline/`）**仅使用 Python 3.9+ 标准库**（`json`, `argparse`, `pathlib`, `re`, `subprocess` 等）；
* 避免引入大型三方包（如 pandas、scikit-learn），保证轻量秒开与跨平台零安装成本。

### 4.3 渲染与 QA 规范
* A4 绝对高度基准固化为 `1122.5px` ($297\text{mm} \times 96\text{DPI} / 25.4$)；
* 任何涉及排版验证与 PDF 导出的改动，必须通过 `scripts/build/run-all-tests.py` 全量测试套件验证。
