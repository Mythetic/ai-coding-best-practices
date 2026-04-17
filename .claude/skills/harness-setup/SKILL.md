---
name: harness-setup
description: 为任何项目一键搭建 Claude Code Harness 配置。当用户提到"搭建 harness"、"配置 harness"、"harness setup"、"初始化 Claude Code"、"项目配置"时自动触发。自动分析项目特征，生成 CLAUDE.md、Rules、Hooks、Skills 全套配置。
version: 2.0.0
---

# Harness Setup Skill

一键为任意项目搭建完整的 Claude Code Harness 配置体系，包括 CLAUDE.md、Rules、Hooks、Skills。

## 触发条件

- 用户说"搭建 harness"、"配置 harness"、"harness setup"
- 用户说"初始化 Claude Code 配置"
- 用户说"帮项目配 Claude"
- 用户提供了一个新项目，希望 Claude Code 能"更了解项目"

## 前置要求

- 当前工作目录在项目根目录下（有 `go.mod`、`package.json`、`Cargo.toml`、`pom.xml` 或 `pyproject.toml` 等项目描述文件之一）
- 项目有 git 初始化

## 重要约束

- **不要修改任何业务代码**，只创建/修改 `.claude/` 目录下的配置文件
- **不要删除已有配置**，只增量补充
- 每个阶段完成后**暂停等待用户确认**，不要一口气跑完全部阶段
- 生成的所有内容必须基于**对项目的实际分析**，禁止使用通用模板硬套
- Rules 文件中的代码示例必须来自**项目真实代码**，不要编造

---

## 执行流程

### Phase 0: 项目探测（自动执行，不等待确认）

**目的：** 识别项目的技术栈、框架、架构模式，为后续阶段提供决策依据。

**步骤：**

1. **识别语言和框架**
   - 扫描项目描述文件：`go.mod` → Go，`package.json` → Node.js，`Cargo.toml` → Rust，`pom.xml` → Java，`pyproject.toml`/`requirements.txt` → Python
   - 识别核心框架：web 框架、ORM、测试框架、日志库
   - 记录 Go/Node/Python/Java/Rust 版本

2. **分析项目结构**
   - 列出顶层目录结构（2 层深度）
   - 识别入口文件（`main.go`、`index.ts`、`app.py` 等）
   - 识别分层模式：MVC？Clean Architecture？DDD？Hexagonal？
   - 识别模块划分

3. **扫描已有配置**
   - 检查是否已有 `CLAUDE.md`、`.claude/rules/`、`.claude/skills/`、`.claude/settings.json`
   - 检查已有的 CI/CD 配置（`.github/workflows/`、`.gitlab-ci.yml` 等）
   - 检查已有的 lint 配置（`.golangci.yml`、`.eslintrc`、`.flake8` 等）
   - 检查已有的 pre-commit hooks
   - 检查已有的 Makefile / scripts

4. **扫描编码模式**
   - 抽样读取 5-10 个核心业务文件，识别：
     - 错误处理模式（返回 error？throw？Result<>？）
     - 日志使用模式（什么库？什么格式？）
     - 数据库使用模式（什么 ORM？查询风格？）
     - 测试模式（什么框架？什么结构？）
   - 统计：总文件数、测试文件数、测试覆盖率

5. **输出探测报告**

向用户展示探测结果，格式：

```
## 项目探测报告

| 维度 | 发现 |
|------|------|
| 语言 | Go 1.24 |
| 框架 | pl_boot（gRPC + HTTP） |
| ORM | GORM |
| 日志 | 项目自有日志库 |
| 测试框架 | testing + testify |
| 架构模式 | 4 层分层（API→Logic→Repository→DB） |
| 模块数 | 6 个 |
| 测试覆盖 | 约 1.5%（3/203 文件有测试） |
| 已有 CLAUDE.md | 有 |
| 已有 Rules | 22 个 |
| 已有 Hooks | 无 |
| 已有 Skills | 12 个（OpenSpec 相关） |

### 建议配置方案
基于探测结果，建议为本项目生成以下配置：
- [ ] CLAUDE.md（补充/更新）
- [ ] 错误处理规范
- [ ] 日志规范
- [ ] 数据库规范
- [ ] 项目结构规范
- [ ] PostToolUse Hook：自动格式化
- [ ] PreToolUse Hook：危险操作拦截
- [ ] Stop Hook：完成度检查
- [ ] /review Skill：代码审查
- [ ] /gen-test Skill：单测生成

确认后进入 Phase 1。
```

**等待用户确认，用户可以勾选/取消配置项。**

---

### Phase 1: 生成 CLAUDE.md

**目的：** 创建或补充项目的 CLAUDE.md，让 Claude 了解项目全貌。

**步骤：**

1. 如果已有 CLAUDE.md，读取并分析缺失部分
2. 如果没有，从项目探测结果生成

**CLAUDE.md 模板：**

```markdown
# CLAUDE.md

## 项目概述
{一段话：项目名称、核心功能、技术栈}

## 常用命令
{从 Makefile/package.json/Cargo.toml 中提取}
- 构建：{command}
- 测试：{command}
- Lint：{command}
- 格式化：{command}

## 架构概览

### 入口
{入口文件路径和说明}

### 目录结构
{关键目录说明，不超过 20 行}

### 分层架构
{分层规则和依赖方向}

### 关键依赖
{核心外部依赖说明}

## 编码约定
{从已有 lint 配置、CI 检查、代码模式中提炼 5-10 条最重要的规范}

## Git 提交规范
{从已有 commit 历史中提炼格式}
```

**校验：**
- 总行数不超过 200 行
- 只包含项目级特有信息，不包含语言通用知识
- 所有命令都经过验证可执行

**展示给用户确认后写入。**

---

### Phase 2: 生成 Rules

**目的：** 从项目真实代码中提炼编码规范，生成 `.claude/rules/` 下的规范文件。

**步骤：**

1. **确定需要生成的规范领域**

根据 Phase 0 的探测结果，从以下候选列表中选择（已有的跳过）：

| 优先级 | 领域 | 生成条件 |
|--------|------|----------|
| P0 | 错误处理 | 项目有统一的错误处理模式 |
| P0 | 日志 | 项目有统一的日志库 |
| P0 | 项目结构 | 项目有明确的分层/模块组织 |
| P1 | 数据库 | 项目使用 ORM |
| P1 | API/接口 | 项目有 RPC/REST 接口 |
| P1 | 测试 | 项目有测试框架 |
| P2 | 安全 | 项目处理敏感数据 |
| P2 | 并发 | 项目使用并发模式 |
| P2 | 代码注释 | 项目有导出符号注释习惯 |
| P3 | Git 提交 | 项目有提交规范 |

2. **对每个领域，从真实代码中提取规范**

方法：
- 从**已有代码**中识别一致的模式（"大多数代码是这样做的"）
- 从**已有 lint 配置**中提取规则
- 从**已有 CI 检查**中提取约束
- 从**已有 Code Review 模板**中提取要点

每个规范文件格式：

```markdown
你是一个专业的{语言}开发助手，所有{领域}必须严格遵循以下规范。

## 【必须】规范条目
- 说明
- 正确示例（来自项目真实代码）
- 错误示例
```

3. **校验**
   - 每个规范文件不超过 200 行
   - 代码示例来自项目真实代码，不是编造的
   - 规范条目与项目已有 lint 规则不冲突

**每生成一个规范文件，展示给用户确认后写入。**

---

### Phase 3: 配置 Hooks

**目的：** 在 `settings.json` 中配置自动化 Hook。

**步骤：**

1. **确定格式化工具**

| 语言 | 格式化命令 |
|------|------------|
| Go | `goimports -w` 或 `gofmt -w` |
| Python | `black` 或 `ruff format` |
| JS/TS | `prettier --write` |
| Rust | `rustfmt` |
| Java | `google-java-format -i` |

检测项目实际安装了哪个工具。

2. **生成 Hook 脚本**

在 `.claude/hooks/` 下创建：

- `auto-format.sh` — 自动格式化（PostToolUse）
- `block-dangerous.sh` — 危险操作拦截（PreToolUse）

脚本内容根据项目语言和已有 lint 配置定制。

3. **生成 settings.json**

如果已有 `settings.json` 或 `settings.local.json`，合并 hooks 配置；否则创建新文件。

配置模板：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": { "tools": ["Write", "Edit"] },
        "type": "command",
        "config": {
          "command": "bash .claude/hooks/auto-format.sh"
        }
      }
    ],
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["Bash"],
          "patterns": ["{项目特有的危险命令模式}"]
        },
        "type": "command",
        "config": {
          "command": "bash .claude/hooks/block-dangerous.sh"
        }
      }
    ],
    "Stop": [
      {
        "matcher": { "all": true },
        "type": "prompt",
        "config": {
          "prompt": "{基于项目规范生成的自检清单}"
        }
      }
    ]
  }
}
```

4. **验证**
   - 手动运行每个 Hook 脚本确认不报错
   - 检查 settings.json 的 JSON 语法

**展示完整配置给用户确认后写入。**

---

### Phase 4: 创建核心 Skills

**目的：** 创建 `/review` 和 `/gen-test` 两个核心 Skill。

**步骤：**

#### 4.1 创建 `/review` Skill

在 `.claude/skills/review/SKILL.md` 中生成代码审查 Skill。

Skill 内容必须基于项目实际情况定制：
- **审查维度**：从 Phase 2 生成的 rules 中提取检查项
- **代码模式**：使用项目真实的正确/错误示例
- **输出格式**：CRITICAL / WARNING / SUGGESTION 三级

SKILL.md 核心结构：

```markdown
---
name: review
description: 对变更代码进行多维度审查。当用户提到"审查"、"review"、"检查代码"时触发。
version: 1.0.0
---

# 代码审查

## 执行流程

### Phase 1: 收集变更
- 无参数 → git diff
- 指定文件 → 读取文件
- 指定 commit → git diff <commit>

### Phase 2: 加载审查标准
读取 .claude/rules/ 下所有规范文件作为审查依据

### Phase 3: 逐维度审查
{根据项目 rules 生成具体的检查维度和检查项}

维度 1: {项目特有维度，如"分层架构合规"}
  - 检查项 A
  - 检查项 B

维度 2: {项目特有维度，如"错误处理规范"}
  - 检查项 A
  - 检查项 B

... 根据项目 rules 数量生成 3-6 个维度

### Phase 4: 生成审查报告

格式：

#### CRITICAL（必须修复）
- **[位置]** 问题描述 → 修复建议 | 违反规范：{rule 文件名}

#### WARNING（应该修复）
- ...

#### SUGGESTION（建议改进）
- ...

#### 审查总结
- 审查文件数：N
- 问题数：N (C 个 Critical / W 个 Warning / S 个 Suggestion)
```

#### 4.2 创建 `/gen-test` Skill

在 `.claude/skills/gen-test/SKILL.md` 中生成测试 Skill。

Skill 内容必须基于项目实际情况定制：
- **测试框架**：项目实际使用的测试框架
- **Mock 策略**：项目实际的依赖注入模式
- **分层策略**：不同层的测试方法不同

SKILL.md 核心结构：

```markdown
---
name: gen-test
description: 为指定函数/文件生成单元测试。当用户提到"写单测"、"生成测试"、"gen test"、"单元测试"时触发。
version: 1.0.0
---

# 单元测试生成

## 执行流程

### Phase 1: 分析目标
- 解析函数签名
- 识别所属层级（决定 Mock 策略）
- 分析业务分支

### Phase 2: 设计用例
{根据项目测试框架和模式定制}

### Phase 3: 生成测试代码
{根据项目的测试约定定制}
- 使用 {项目的测试框架}
- {项目的测试文件命名规范}
- {项目的 Mock 模式}

### Phase 4: 运行验证
- 编译检查
- 运行测试
- 覆盖率报告
```

**两个 Skill 都展示给用户确认后写入。**

---

### Phase 5: 生成总结报告

**目的：** 汇总所有生成的配置，输出使用指南。

**输出格式：**

```markdown
## Harness 配置完成

### 生成的文件清单

| 类型 | 文件 | 说明 |
|------|------|------|
| 上下文 | CLAUDE.md | 项目全貌（新建/更新） |
| 规范 | .claude/rules/{name}.md × N | N 个领域规范 |
| Hook | .claude/hooks/auto-format.sh | 自动格式化 |
| Hook | .claude/hooks/block-dangerous.sh | 危险操作拦截 |
| 配置 | .claude/settings.json | Hooks 配置 |
| Skill | .claude/skills/review/SKILL.md | 代码审查 |
| Skill | .claude/skills/gen-test/SKILL.md | 单测生成 |

### 使用方式

- **代码审查**：输入 `/review` 或说"帮我审查代码"
- **生成测试**：输入 `/gen-test` 或说"帮这个函数写单测"
- **自动格式化**：无需操作，编辑文件后自动执行
- **危险拦截**：无需操作，执行危险命令时自动拦截

### 后续建议

根据使用情况，可以继续添加：
- `/gen-crud` 脚手架 Skill
- `/check-arch` 架构检查 Skill
- `/db-review` 数据库审查 Skill
- 更多领域的 Rules
```

---

## 各语言适配要点

### Go 项目

- 格式化：`goimports -w`（优先）或 `gofmt -w`
- Lint：从 `.golangci.yml` 提取规则
- 测试：`go test -v -run TestXxx ./...`
- 错误处理：检查 error 返回值处理模式
- 特有规范：goroutine 管理、defer 使用、interface 设计

### Python 项目

- 格式化：`black`（优先）或 `ruff format`
- Lint：从 `pyproject.toml`/`.flake8`/`ruff.toml` 提取
- 测试：`pytest -v`
- 错误处理：检查 try/except 模式、自定义异常
- 特有规范：类型标注、async/await 模式、import 分组

### Node.js/TypeScript 项目

- 格式化：`prettier --write`
- Lint：从 `.eslintrc`/`eslint.config.js` 提取
- 测试：`jest`/`vitest`/`mocha`
- 错误处理：检查 try/catch 模式、错误类层级
- 特有规范：ESM vs CJS、依赖管理、环境变量处理

### Rust 项目

- 格式化：`rustfmt`
- Lint：从 `clippy.toml` 提取
- 测试：`cargo test`
- 错误处理：检查 Result/Option 使用模式
- 特有规范：所有权模型、生命周期、unsafe 使用

### Java 项目

- 格式化：`google-java-format`
- Lint：从 `checkstyle.xml`/`pmd.xml` 提取
- 测试：`maven test`/`gradle test`
- 错误处理：检查异常处理模式、自定义异常层级
- 特有规范：Spring 注解、依赖注入、日志框架

---

## 边界情况处理

### 已有完整 Harness 的项目

如果探测到项目已有完整配置（CLAUDE.md + Rules + Hooks + Skills），输出差距分析报告而非重新生成：

```
项目已有较完整的 Harness 配置。以下是差距分析：

| 维度 | 现状 | 建议补充 |
|------|------|----------|
| Rules | 22 个，覆盖 13 领域 | 缺少测试规范、RPC 调用规范 |
| Hooks | 无 | 建议添加自动格式化和危险拦截 |
| Skills | 12 个（均为 OpenSpec） | 建议添加 /review 和 /gen-test |
```

### Monorepo 项目

如果检测到 monorepo（多个子项目），询问用户：
- 为整个 repo 生成全局配置？
- 只为某个子项目生成配置？

### 无法识别技术栈

如果项目根目录没有标准的项目描述文件，要求用户手动指定：
- 使用的编程语言
- 构建命令
- 测试命令
- 格式化命令
