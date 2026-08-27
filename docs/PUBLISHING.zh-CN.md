# NPM 构建、发布与版本更新指南

本文档详细说明如何将 **`knowme-careerforge-skill`** 打包构建、发布以及迭代更新至官方 [NPM Registry](https://www.npmjs.com/)。

---

## 1. 准备工作

首次发布前需确保：

1. **注册 NPM 账号**：在 [npmjs.com](https://www.npmjs.com/) 注册账号；
2. **在本地终端登录**：
   ```bash
   npm login
   ```
3. **验证登录状态**：
   ```bash
   npm whoami
   ```

---

## 2. 打包文件白名单与架构

发布时，NPM 将严格按照 `package.json` 中的 `"files"` 白名单进行打包分发：

```json
"files": [
  "bin",        // Standalone 零依赖可执行入口 (bin/knowme.js)
  "dist",       // 预编译的 TypeScript CLI 产物 (dist/cli/src/index.js)
  "src",        // 单一事实源：knowledge(知识库), templates(模板), workflows, references
  "scripts",    // 核心引擎工具链 (search, analyze, instantiate, validate, render)
  "agents",     // 多平台配置文件 (Claude, Codex, Cursor, Windsurf, Gemini, OpenCode)
  "SKILL.md",   // Agent 核心推理与执行契约
  "skill.json"  // Skill 元数据清单
]
```

---

## 3. 一键自动化发布流程

项目内置了发布自动化引擎（`scripts/build/release.py`），自动完成版本号同步、知识库编译、画廊刷新、TypeScript 编译、全量测试质检与打包预检。

### 发布新版本：

```bash
npm run release -- <version>
# 或直接运行：
python3 scripts/build/release.py <version>
```

该脚本将自动执行：
1. **多文件版本号同步**：自动对齐 `package.json`、`pyproject.toml`、`skill.json` 与 `cli/package.json`；
2. **知识库索引编译**：运行 `scripts/build/build-knowledge.py` 生成最新索引；
3. **模板画廊生成**：运行 `scripts/build/build-gallery.py` 刷新静态预览画廊；
4. **CLI 编译**：运行 `npm run build` 将 TypeScript 编译至 `dist/`；
5. **全量测试质检**：运行 `scripts/build/run-all-tests.py` 执行 24 项测试（确保 100% 通过）；
6. **NPM 打包预检**：运行 `npm pack --dry-run` 检查打包文件清单与解压体积。

---

## 4. 正式发布至 NPM 镜像源

在 release 脚本通过所有测试后，执行以下标准命令：

```bash
# 1. 提交代码并打上 Git Tag
git add .
git commit -m "chore(release): bump version to v<version>"
git tag v<version>
git push origin main --tags

# 2. 正式发布至公共 NPM 注册表
npm publish --access public
```

---

## 5. 验证发布的 NPM 包

发布成功后，可在任何项目或终端中直接免安装验证：

```bash
# 查看 NPM 注册表元数据
npm view knowme-careerforge-skill

# 测试 npx 免安装一键执行
npx knowme-careerforge-skill@latest list
npx knowme-careerforge-skill@latest search "AI Agent Engineer"
```

---

## 6. 日常版本更新指南

| 更新类型 | 触发命令 | 版本号变化示例 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **Patch (补丁版本)** | `npm run release -- 0.0.2` | `0.0.1` ➔ `0.0.2` | 修复 Bug、修正文档错别字、微调模板 CSS 变量 |
| **Minor (次版本)** | `npm run release -- 0.1.0` | `0.0.1` ➔ `0.1.0` | 新增简历模板、新增岗位画像、新增 CLI 子命令 |
| **Major (主版本)** | `npm run release -- 1.0.0` | `0.1.0` ➔ `1.0.0` | 达成生产里程碑、底层 Schema 破坏性重构 |
