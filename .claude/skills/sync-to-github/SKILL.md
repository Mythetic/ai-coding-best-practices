---
name: sync-to-github
description: |
  当用户要求将 skill、rule、command、agent 等 AI 编码助手配置同步到 GitHub 时触发。
  触发词：同步到 GitHub、推到 GitHub、sync to github、同步 xxx 到 GitHub、把 xxx 推到 GitHub。
  用户会指定要同步的内容（名称或路径），自动完成脱敏、复制、提交、推送。
---

# 同步配置到 GitHub

将指定的 AI 编码助手配置（skill、rule、command、agent 等）脱敏后同步到 GitHub 仓库。

## 目标仓库

- 本地路径：`~/github/ai-coding-best-practices`
- 远程仓库：`https://github.com/Mythetic/ai-coding-best-practices`
- 配置目录：`.claude/`（rules、commands、skills 子目录）

## 执行流程

### 1. 确定同步源

从用户消息中提取要同步的内容，支持以下方式：
- **按名称**：如"同步 skill-creator 到 GitHub"，自动在以下位置查找：
  - `~/.claude/skills/{name}/`（全局 skill）
  - `{当前项目}/.claude/skills/{name}/`（项目 skill）
  - `{当前项目}/.codebuddy/skills/{name}/`（CodeBuddy skill）
  - `~/.claude/rules/{name}`（全局 rule）
  - `{当前项目}/.claude/rules/{name}`（项目 rule）
  - `{当前项目}/.codebuddy/rules/{name}`（CodeBuddy rule）
  - 同理适用于 commands、agents 等目录
- **按路径**：如"同步 ~/.claude/skills/xxx 到 GitHub"，直接使用指定路径
- **按类型批量**：如"把当前项目的所有 rules 同步到 GitHub"

如果找不到，向用户确认路径。

### 2. 读取源文件内容

读取要同步的所有文件内容，包括子目录中的文件（如 scripts/、agents/ 等）。

### 3. 脱敏处理

对所有文件内容执行以下脱敏替换（大小写不敏感匹配）：

**必须替换的公司/项目信息：**

| 原始内容 | 替换为 |
|---------|--------|
| `电子签` | 移除或替换为通用描述 |
| `tsign` | `myproject` 或移除 |
| `腾讯` / `tencent` | 移除 |
| `企业微信` / `wecom` | 移除 |
| `*.woa.com` | `example.com` |
| `*.code.oa.com` | `example.com` |
| `git.woa.com/...` | `example.com/myproject/...` |
| `git.code.oa.com/...` | `example.com/myproject/...` |
| `signature`（作为项目名时） | `myproject` 或通用名 |
| `TAI_IT_TOKEN` | `MCP_AUTH_TOKEN` |
| `tai.it.woa.com` | `your-auth-platform.example.com` |
| `CodeBuddy（内网版）` | `AI coding assistant` |

**判断原则：**
- 如果内容是通用技术知识（如 GORM 用法、Go 规范），保留原内容，仅替换公司特定引用
- 如果内容强依赖内网基础设施（如特定内网 URL、内部工具），替换为占位符并加注释说明
- 保持文件的技术完整性和可用性

### 4. 确定目标路径

根据源文件类型映射到目标仓库的对应目录：

| 源类型 | 目标路径 |
|--------|---------|
| skill | `~/github/ai-coding-best-practices/.claude/skills/{name}/` |
| rule | `~/github/ai-coding-best-practices/.claude/rules/{name}` |
| command | `~/github/ai-coding-best-practices/.claude/commands/{name}` |
| agent | `~/github/ai-coding-best-practices/.claude/agents/{name}` |

如果是 `.codebuddy/` 格式的源文件，需要适配为 `.claude/` 格式：
- frontmatter 中的 `type: always` 替换为 `description` + `globs` 格式
- 移除 `# 注意不要修改本文头文件，如修改，CodeBuddy（内网版）将按照默认逻辑设置` 这类注释

### 5. 写入目标文件

将脱敏后的内容写入目标仓库对应路径。如果目标文件已存在，覆盖更新。

### 6. 更新 CLAUDE.md（如有新增）

如果是新增的文件（非更新），需要检查 `~/github/ai-coding-best-practices/CLAUDE.md` 中的目录结构描述是否需要更新。

### 7. Git 提交并推送

```bash
cd ~/github/ai-coding-best-practices
git add -A
git commit -m "sync: {简要描述同步了什么}"
git push origin master
```

- 提交信息格式：`sync: add {name} skill` 或 `sync: update {name} rule` 等
- 禁止携带 AI 相关 Co-Authored-By 信息

## 规则

### 必须

- 同步前必须完整读取源文件，确保不遗漏任何子文件
- 脱敏必须彻底，执行完脱敏后用 grep 验证无残留（搜索 tsign、tencent、腾讯、电子签、woa.com、code.oa.com 等关键词）
- 提交前 `git diff` 展示变更摘要给用户确认
- 推送后告知用户 GitHub 仓库链接

### 禁止

- 禁止同步包含密钥、Token、密码等敏感凭证的文件
- 禁止同步 sessionid、.env 等敏感文件
- 禁止在未完成脱敏验证的情况下推送
