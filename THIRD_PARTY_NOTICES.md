# Third-Party Notices & Open Source Provenance

**KnowMe CareerForge** is released under the **MIT License**.

This project incorporates architectural concepts, data structures, and methodology inspired by the following open-source projects:

---

## 1. Reference Projects & Intellectual Provenance

### 1. `repo-to-resume-tailor`
- **Core Inspiration**: Target-Role / JD Matching Modes, L1~L3 Evidence Hierarchy, Anti-Hallucination Discipline, and automated Codebase / Repository Fact Extraction.
- **Project Link**: Reference implementation for codebase evidence mining.

### 2. `ui-ux-pro-max-skill`
- **Core Inspiration**: Single Source of Truth architecture, Design Tokens CSS variable hierarchy, Multi-Agent native distribution ecosystem (`skill.json`, platform adapters, CLI toolchain).
- **License**: MIT License

### 3. `geekcompany/ResumeSample`
- **Core Inspiration**: Tech role competency mapping, FAB (Feature-Advantage-Benefit) evidence structure, high-frequency technical keywords analysis.
- **License**: MIT License
- **Transformation Note**: All original markdown samples were offline preprocessed and restructured into standard JSON knowledge profiles (`src/knowledge/roles/*.json`). No raw documents are executed dynamically at runtime.

### 4. `mmmlllnnn/ResumeCollection`
- **Core Inspiration**: Layout composition ratios (single-column, 32:68 split, executive banner, modern table grid) and visual density principles.
- **Transformation Note**: All legacy `.doc` and `.docx` binary files were completely abandoned. All templates in `src/templates/` are 100% freshly written from scratch using modern semantic HTML5 and CSS3 Paged Media.

---

## 2. Typography & Fonts Notice

All templates in KnowMe CareerForge utilize native cross-platform system font fallbacks:
- **English**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `Helvetica Neue`, `Arial`, `sans-serif`
- **Chinese**: `"PingFang SC"`, `"Hiragino Sans GB"`, `"Microsoft YaHei"`, `"WenQuanYi Micro Hei"`, `sans-serif`

No proprietary or unlicensed binary font files are bundled in this repository.
