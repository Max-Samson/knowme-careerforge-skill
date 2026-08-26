# Workflow 5: Forge Resume (简历工程与修改场排版)

> **目标：以 HTML 为唯一修改场，填充结构化内容，调校 Design Tokens 实现像素级排版。**

---

## 1. 模板检索与修改场实例化

1. **执行模板检索**：
   ```bash
   python3 scripts/template/search-template.py "<Target Role>" --style "<minimal|modern|executive|classic>" --target-pages 1
   ```
2. **实例化中间修改场**：
   ```bash
   python3 scripts/template/instantiate-resume.py --template <template_id> --keywords "Python,LLM,RAG,FastAPI" --output workspace/resume.html
   ```

## 2. 修改场编辑规范

1. **内容填充**：
   - 保持语义化标签结构：`h1.candidate-name`, `p.job-target`, `section.resume-section`, `div.experience-item`, `ul.bullet-list`。
2. **Design Tokens 视觉调校**：
   - 全局间距：`--resume-space-section`, `--resume-space-item`, `--resume-space-bullet`。
   - 正文字号：`--resume-font-size-body`（标准 `9.2pt`，紧凑可微调至 `8.8pt`）。
   - 色彩体系：`--resume-color-accent`, `--resume-color-primary`。
