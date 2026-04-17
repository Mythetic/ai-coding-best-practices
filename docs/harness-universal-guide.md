# Claude Code Harness 通用方法论

> 一份语言无关、框架无关的 Harness 搭建指南。
> 适用于任何使用 Claude Code 的软件项目。

---

## 目录

- [一、什么是 Harness](#一什么是-harness)
- [二、Harness 三层架构](#二harness-三层架构)
- [三、第一层：上下文层（CLAUDE.md + Rules）](#三第一层上下文层claudemd--rules)
- [四、第二层：自动化层（Hooks）](#四第二层自动化层hooks)
- [五、第三层：能力层（Skills）](#五第三层能力层skills)
- [六、通用 Skill 模式库](#六通用-skill-模式库)
- [七、通用 Hook 模式库](#七通用-hook-模式库)
- [八、Settings.json 完整配置参考](#八settingsjson-完整配置参考)
- [九、搭建流程：从零到完整 Harness 的 6 步](#九搭建流程从零到完整-harness-的-6-步)
- [十、度量与演进](#十度量与演进)
- [附录 A：Skill 文件规范](#附录-askill-文件规范)
- [附录 B：Hook 脚本规范](#附录-bhook-脚本规范)
- [附录 C：常见问题](#附录-c常见问题)

---

## 一、什么是 Harness

Harness 是 Claude Code 围绕一个具体项目建立的**配置体系**，目的是让 Claude 从"通用 AI 助手"变成"深度了解你项目的专业开发同事"。

一个完整的 Harness 包含：

```
┌─────────────────────────────────────────────────────┐
│                   Claude Code 会话                   │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  第一层：上下文层                              │  │
│  │  CLAUDE.md + .claude/rules/                   │  │
│  │  "Claude 知道什么"                             │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  第二层：自动化层                              │  │
│  │  Hooks (PreToolUse / PostToolUse / Stop)      │  │
│  │  "Claude 做事时自动执行什么"                    │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  第三层：能力层                                │  │
│  │  Skills (.claude/skills/)                     │  │
│  │  "Claude 被要求时能做什么"                      │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**核心原则：** 上下文层是"法律"，自动化层是"执法"，能力层是"专业服务"。三层缺一不可。

---

## 二、Harness 三层架构

| 层 | 机制 | 加载时机 | Token 成本 | 核心作用 |
|----|------|----------|------------|----------|
| 上下文层 | CLAUDE.md、`.claude/rules/*.md` | 每次会话自动加载 | 持续占用 | 告诉 Claude 项目的技术栈、架构、编码规范 |
| 自动化层 | `settings.json` 中的 hooks | 工具调用前/后自动触发 | 极低（仅触发时） | 自动格式化、拦截违规、完成度检查 |
| 能力层 | `.claude/skills/*/SKILL.md` | 用户关键词触发时加载 | 按需加载 | 代码审查、测试生成、脚手架等专业流程 |

### 三层之间的关系

```
用户说："帮我审查这段代码"
       │
       ▼
  ┌──────────┐   触发
  │ Skill 层 │ ◄──── 关键词匹配 "审查"
  │ /review  │
  └────┬─────┘
       │ Skill 读取 rules/ 中的规范作为审查标准
       ▼
  ┌──────────┐
  │ 上下文层 │   提供审查依据
  │ rules/*  │
  └──────────┘
       │ Claude 修改代码后
       ▼
  ┌──────────┐   自动触发
  │ Hook 层  │ ◄──── PostToolUse
  │ gofmt    │
  └──────────┘
```

---

## 三、第一层：上下文层（CLAUDE.md + Rules）

### 3.1 CLAUDE.md 的定位

CLAUDE.md 是项目的**入口文档**，Claude 每次会话都会自动加载。它应该包含：

```markdown
# CLAUDE.md

## 项目概述
一段话说清：这是什么项目、用什么技术栈、核心业务是什么

## 常用命令
make build / make test / make lint 等

## 架构概览
- 入口在哪里
- 分层是什么
- 模块划分
- 关键依赖

## 编码约定摘要
- 最重要的 5-10 条规范（详细规范放 rules/）
- 容易犯错的点

## Git 提交规范
- 消息格式
- 禁止事项
```

**最佳实践：**
- CLAUDE.md 控制在 200 行以内（它始终在上下文中，太长浪费 token）
- 详细规范放到 `.claude/rules/` 下的独立文件
- CLAUDE.md 只放"最重要的、最容易忘记的"内容

### 3.2 Rules 的组织原则

`.claude/rules/` 下的规范文件会自动加载到上下文中。组织原则：

#### 按领域拆分

每个文件聚焦一个领域，文件名用 `{项目名}_{领域}.md` 格式：

```
.claude/rules/
├── myproject_error.md          # 错误处理规范
├── myproject_log.md            # 日志规范
├── myproject_db.md             # 数据库规范
├── myproject_api.md            # API 接口规范
├── myproject_test.md           # 测试规范
├── myproject_security.md       # 安全规范
└── myproject_project_structure.md  # 项目结构规范
```

#### 每个规范文件的结构

```markdown
你是一个专业的{语言}开发助手，所有{领域}必须严格遵循以下规范。

## 【必须】规范条目 1
- 描述
- 正确示例（代码块）
- 错误示例（代码块）

## 【必须】规范条目 2
...

## 【推荐】规范条目 3
...
```

#### 通用规范领域清单

无论什么语言/框架，以下领域都值得建立规范：

| 优先级 | 领域 | 说明 | 示例内容 |
|--------|------|------|----------|
| P0 | 错误处理 | 如何创建、传播、处理错误 | 错误类型选择、错误包装、用户可见消息 |
| P0 | 日志 | 日志库、级别、格式、安全 | 禁用 print/console.log、必须传 context |
| P0 | 项目结构 | 目录组织、分层规则、依赖方向 | 分层调用链、禁止跨层/反向依赖 |
| P1 | 数据库 | ORM 使用、查询规范、迁移规则 | 软删除、显式表名、参数化查询 |
| P1 | API/接口 | 命名、版本、请求响应格式 | RESTful/gRPC 命名动词、分页参数 |
| P1 | 测试 | 测试结构、Mock 模式、覆盖率标准 | 表驱动测试、接口 Mock |
| P2 | 安全 | 输入校验、敏感数据、权限检查 | 脱敏日志、参数校验位置 |
| P2 | 并发 | 并发原语、goroutine/线程管理 | 禁止裸启线程、context 传递 |
| P2 | 缓存 | key 命名、TTL、一致性策略 | 缓存穿透/击穿处理 |
| P2 | 消息队列 | Topic 命名、消费者规范 | 幂等消费、异常告警 |
| P3 | 代码注释 | 注释位置、格式、内容要求 | 文件注释、导出符号注释 |
| P3 | 命名 | 变量/函数/文件/包命名规范 | 驼峰/蛇形、缩写规则 |
| P3 | Git 提交 | 消息格式、禁止事项 | conventional commits、禁止 AI 署名 |

### 3.3 全局 vs 项目级配置

```
~/.claude/CLAUDE.md              # 全局规范（所有项目共享）
~/.claude/rules/                 # 全局规范文件

项目根目录/CLAUDE.md             # 项目级规范
项目根目录/.claude/rules/        # 项目级规范文件
```

**优先级：** 项目级 > 全局级

**全局适合放什么：**
- 语言通用编码规范（如 Go 编码规范、Python PEP8 等）
- Git 提交规范
- 开发前必做步骤

**项目级适合放什么：**
- 项目特有的架构规范
- 项目特有的错误处理模式
- 业务相关的安全规范

---

## 四、第二层：自动化层（Hooks）

### 4.1 Hook 类型全览

| Hook 类型 | 触发时机 | 最佳用途 |
|-----------|----------|----------|
| `PreToolUse` | Claude 调用工具**之前** | 拦截危险操作、校验写入内容合规 |
| `PostToolUse` | 工具执行**之后** | 自动格式化、后置校验、结果增强 |
| `Stop` | Claude 准备结束工作时 | 强制完成度检查、提醒遗漏 |
| `PreSubagentUse` | 生成子 Agent 之前 | 控制任务委派策略 |
| `SubagentStop` | 子 Agent 停止时 | 防止子 Agent 过早退出 |

### 4.2 Hook 配置详解

Hook 在 `settings.json`（项目级或全局级）中配置：

```json
{
  "hooks": {
    "HookType": [
      {
        "matcher": { ... },     // 匹配条件：哪些操作触发此 Hook
        "type": "command",       // 类型："command"（脚本）或 "prompt"（LLM 判断）
        "config": { ... }        // 具体配置
      }
    ]
  }
}
```

#### Matcher（匹配器）

```json
// 匹配特定工具
"matcher": { "tools": ["Write", "Edit"] }

// 匹配文件模式
"matcher": { "tools": ["Write"], "patterns": [".*\\.go$"] }

// 匹配命令内容
"matcher": { "tools": ["Bash"], "patterns": ["rm -rf", "DROP TABLE"] }

// 匹配所有操作
"matcher": { "all": true }
```

#### Command 类型 Hook

执行一个外部脚本，通过退出码和 JSON 输出控制行为：

```json
{
  "matcher": { "tools": ["Write"], "patterns": [".*\\.go$"] },
  "type": "command",
  "config": {
    "command": "bash .claude/hooks/post-write-go.sh"
  }
}
```

脚本输出格式：

```json
{
  "decision": "approve",     // "approve" | "block" | "warn"
  "reason": "阻断原因",
  "feedback": "给 Claude 的修改建议",
  "continue": true,          // false = 最强阻断
  "suppressOutput": false
}
```

退出码：`0` = 通过，`1` = 警告（不阻断），`2` = 阻断

#### Prompt 类型 Hook

让 Claude 自身做判断（适合语义级检查）：

```json
{
  "matcher": { "tools": ["Write"], "patterns": ["internal/.*\\.go$"] },
  "type": "prompt",
  "config": {
    "prompt": "检查这段代码是否遵循分层架构：API 层是否只做参数校验和转发？Logic 层是否不直接操作数据库？"
  }
}
```

### 4.3 推荐的 Hook 配置模板

以下是适用于大多数项目的 Hook 配置基线：

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
          "patterns": ["DROP TABLE", "TRUNCATE", "rm -rf", "git push.*--force"]
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
          "prompt": "停止前请自检：1) 新增的导出符号是否有文档注释？2) 错误是否都被处理？3) 是否需要补充测试？4) 代码格式是否正确？"
        }
      }
    ]
  }
}
```

---

## 五、第三层：能力层（Skills）

### 5.1 Skill 的定位

Skill 是**按需加载的领域知识包**。与 Rules 的区别：

| 维度 | Rules | Skills |
|------|-------|--------|
| 加载时机 | 每次会话自动加载 | 用户触发时加载 |
| Token 成本 | 持续占用 | 按需占用 |
| 内容类型 | 规范约束（"不要这样做"） | 执行流程（"按这个步骤做"） |
| 适合放什么 | 编码规范、命名规则 | 代码审查流程、测试生成流程、脚手架模板 |

### 5.2 Skill 三层加载模型

```
Tier 1: Metadata（始终在上下文）
  ┌─────────────────────────────┐
  │ ---                         │
  │ name: my-skill              │  ← 约 100 tokens
  │ description: 做什么，触发词   │
  │ ---                         │
  └─────────────────────────────┘

Tier 2: Body（触发时加载）
  ┌─────────────────────────────┐
  │ # Skill 标题                │
  │                             │  ← 约 500-2000 tokens
  │ ## 执行流程                  │
  │ ## 检查要点                  │
  │ ## 输出格式                  │
  └─────────────────────────────┘

Tier 3: Resources（按需加载）
  ┌─────────────────────────────┐
  │ references/                 │
  │ scripts/                    │  ← 变长，按需读取
  │ templates/                  │
  └─────────────────────────────┘
```

### 5.3 Skill 文件结构

```
.claude/skills/my-skill/
├── SKILL.md              # 必须：Skill 定义文件
├── references/            # 可选：参考文档
│   ├── patterns.md
│   └── examples.md
├── scripts/               # 可选：辅助脚本
│   └── check.sh
└── templates/             # 可选：代码模板
    └── module-template/
```

### 5.4 SKILL.md 标准格式

```markdown
---
name: skill-name
description: 一句话描述功能。包含触发关键词。当用户提到"关键词A"、"关键词B"时触发。
version: 1.0.0
---

# Skill 标题

## 触发条件
- 用户说"..."时触发
- 用户说"..."时触发

## 前置要求
- 需要什么工具/环境
- 需要读取什么配置

## 执行流程

### Phase 1: 分析
1. 做什么
2. 做什么

### Phase 2: 执行
1. 做什么
2. 做什么

### Phase 3: 验证
1. 做什么
2. 做什么

## 输出格式
描述最终输出的结构和内容

## 约束
- 不要做什么
- 必须做什么
```

---

## 六、通用 Skill 模式库

以下是任何项目都可以复用的 Skill 模式。每个模式描述了 Skill 的核心流程，具体实现需根据项目的技术栈和规范调整。

### 模式 1：代码审查 Skill（`/review`）

**适用场景：** 任何有编码规范的项目

**核心流程：**

```
Phase 1: 收集变更
  ├── 无参数 → git diff（未提交的变更）
  ├── 指定文件 → 读取指定文件
  └── 指定 commit → git diff <commit>

Phase 2: 加载规范
  ├── 读取 .claude/rules/ 下所有规范文件
  ├── 读取 CLAUDE.md 中的编码约定
  └── 识别变更文件所属的领域（DB？API？Logic？）

Phase 3: 逐维度审查
  ├── 架构合规：分层是否正确？依赖方向？
  ├── 规范遵循：命名？注释？格式？
  ├── 错误处理：是否完整？模式是否正确？
  ├── 安全风险：敏感数据？输入校验？
  └── 性能隐患：N+1 查询？循环内 I/O？

Phase 4: 生成报告
  ├── CRITICAL（必须修复）
  ├── WARNING（应该修复）
  └── SUGGESTION（建议改进）
  每项包含：位置 + 问题描述 + 修复建议 + 违反的规范条目
```

### 模式 2：测试生成 Skill（`/gen-test`）

**适用场景：** 任何有测试框架的项目

**核心流程：**

```
Phase 1: 分析目标
  ├── 解析函数签名（参数、返回值、接口依赖）
  ├── 识别函数所属层级（决定 Mock 策略）
  └── 分析业务逻辑分支（if/switch/error 路径）

Phase 2: 设计用例
  ├── 正常路径（Happy Path）
  ├── 参数边界（空值、零值、最大值）
  ├── 错误路径（依赖返回错误）
  └── 业务分支（每个 if/switch 分支至少一个用例）

Phase 3: 生成代码
  ├── 使用项目的测试框架和模式
  ├── 表驱动测试 / 子测试
  ├── Mock 实现（基于接口）
  └── 断言（错误类型、返回值、调用次数）

Phase 4: 验证
  ├── 编译检查
  ├── 运行测试
  └── 覆盖率报告
```

### 模式 3：CRUD 脚手架 Skill（`/gen-crud`）

**适用场景：** 分层架构的后端服务

**核心流程：**

```
Phase 1: 收集信息
  ├── 模块名
  ├── 资源名（表名）
  ├── 字段列表（名称 + 类型 + 注释）
  └── 需要的接口（Create/Describe/Modify/Delete/List）

Phase 2: 生成代码（自底向上）
  ├── DB Model（字段映射、表名方法）
  ├── Repository（CRUD 方法、软删除）
  ├── Logic（业务骨架、参数校验）
  ├── API（接口实现、错误转换）
  └── 注册代码（服务注册入口）

Phase 3: 生成配套
  ├── 接口定义（Proto/OpenAPI）
  ├── 基础单测
  └── 文件注释

Phase 4: 验证
  ├── 编译通过
  └── 架构合规（依赖方向正确）
```

### 模式 4：架构合规检查 Skill（`/check-arch`）

**适用场景：** 有明确架构规范的项目

**核心流程：**

```
Phase 1: 扫描项目结构
  ├── 列出所有模块及其分层目录
  └── 解析每个文件的 import 关系

Phase 2: 检查依赖方向
  ├── 正向依赖 ✅（上层 → 下层）
  ├── 反向依赖 ❌（下层 → 上层）
  ├── 跨模块 internal ❌
  └── 导出层反向依赖 ❌（entity → logic）

Phase 3: 检查规范违规
  ├── 读取 rules/ 中的规范
  ├── 扫描代码中的违规模式
  └── 分类统计

Phase 4: 生成合规报告
  ├── 依赖关系图（ASCII）
  ├── 违规列表（按严重级别）
  └── 修复建议
```

### 模式 5：数据库审查 Skill（`/db-review`）

**适用场景：** 有数据库操作的后端项目

**核心流程：**

```
Phase 1: 收集变更
  ├── DDL 语句（CREATE/ALTER TABLE）
  ├── Repository/DAO 代码
  └── ORM Model 定义

Phase 2: 规范检查
  ├── 建表模板合规（字符集、主键、公共字段）
  ├── 查询安全（参数化、软删除条件）
  ├── 写操作安全（禁物理删除、禁 struct 更新）
  ├── 性能（索引、分表逻辑）
  └── 命名（表名、字段名）

Phase 3: 生成报告
```

### 模式 6：国际化改造 Skill（`/i18n`）

**适用场景：** 需要多语言支持的项目

**核心流程：**

```
Phase 1: 扫描硬编码文案
  ├── 定位接口返回入口
  ├── 追溯 message 来源
  └── 与已有翻译 key 做语义匹配

Phase 2: 生成翻译 key
  ├── 按模块归属确定命名
  ├── 复用已有通用翻译
  └── 列出改造清单

Phase 3: 更新翻译文件
  ├── 合并新 key 到语言文件
  └── 生成常量代码

Phase 4: 替换代码
  ├── 用翻译函数替换硬编码
  └── 验证编译通过
```

---

## 七、通用 Hook 模式库

### Hook 1：自动格式化（PostToolUse）

**适用语言和工具：**

| 语言 | 格式化命令 |
|------|------------|
| Go | `goimports -w $FILE` 或 `gofmt -w $FILE` |
| Python | `black $FILE` 或 `ruff format $FILE` |
| JavaScript/TypeScript | `prettier --write $FILE` |
| Rust | `rustfmt $FILE` |
| Java | `google-java-format -i $FILE` |

**通用脚本模板：**

```bash
#!/bin/bash
# .claude/hooks/auto-format.sh
FILE="$CLAUDE_FILE_PATH"

case "$FILE" in
  *.go)     goimports -w "$FILE" 2>/dev/null || gofmt -w "$FILE" ;;
  *.py)     black "$FILE" 2>/dev/null || true ;;
  *.ts|*.js|*.tsx|*.jsx) prettier --write "$FILE" 2>/dev/null || true ;;
  *.rs)     rustfmt "$FILE" 2>/dev/null || true ;;
esac

echo '{"decision":"approve"}'
exit 0
```

### Hook 2：危险操作拦截（PreToolUse）

```bash
#!/bin/bash
# .claude/hooks/block-dangerous.sh
INPUT="$1"

# 检查破坏性 SQL
if echo "$INPUT" | grep -iE "DROP TABLE|TRUNCATE TABLE" > /dev/null; then
  echo '{"decision":"block","reason":"禁止 DROP/TRUNCATE 操作","feedback":"如需废弃表请使用 RENAME TABLE","continue":false}'
  exit 2
fi

# 检查强制推送
if echo "$INPUT" | grep -E "git push.*--force|git push.*-f" > /dev/null; then
  echo '{"decision":"block","reason":"禁止 force push","feedback":"请使用 --force-with-lease 或正常推送","continue":false}'
  exit 2
fi

# 检查危险删除
if echo "$INPUT" | grep -E "rm -rf /" > /dev/null; then
  echo '{"decision":"block","reason":"禁止删除根目录","continue":false}'
  exit 2
fi

echo '{"decision":"approve"}'
exit 0
```

### Hook 3：文件大小限制（PreToolUse）

```bash
#!/bin/bash
# .claude/hooks/check-file-size.sh
FILE="$CLAUDE_FILE_PATH"

if [ -f "$FILE" ]; then
  LINE_COUNT=$(wc -l < "$FILE")
  MAX_LINES=800

  if [ "$LINE_COUNT" -gt "$MAX_LINES" ]; then
    echo "{\"decision\":\"warn\",\"reason\":\"文件已有 ${LINE_COUNT} 行，超过 ${MAX_LINES} 行限制\",\"feedback\":\"考虑拆分为多个文件\"}"
    exit 1
  fi
fi

echo '{"decision":"approve"}'
exit 0
```

### Hook 4：敏感信息检查（PreToolUse）

```bash
#!/bin/bash
# .claude/hooks/check-secrets.sh
INPUT="$1"

# 检查常见密钥模式
if echo "$INPUT" | grep -iE "password\s*=|secret\s*=|api_key\s*=|token\s*=" | grep -v "// " | grep -v "# " > /dev/null; then
  echo '{"decision":"warn","reason":"检测到可能的硬编码密钥","feedback":"请使用环境变量或配置中心管理密钥"}'
  exit 1
fi

echo '{"decision":"approve"}'
exit 0
```

### Hook 5：完成度检查（Stop）

```json
{
  "matcher": { "all": true },
  "type": "prompt",
  "config": {
    "prompt": "在结束工作前，请确认以下几点：1) 新增的导出符号是否都有文档注释？2) 所有错误是否都被正确处理？3) 是否需要补充或更新测试？4) 代码格式是否正确？5) 是否有安全风险（硬编码密钥、SQL 注入等）？如果有遗漏，请先完成再停止。"
  }
}
```

---

## 八、Settings.json 完整配置参考

### 8.1 文件位置与优先级

```
优先级从高到低：
1. 项目级：{项目根目录}/.claude/settings.json
2. 用户级：~/.claude/settings.json
3. 命令行参数
4. 默认值
```

### 8.2 完整配置模板

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Bash(make *)",
      "Bash(go test *)",
      "Bash(npm test *)",
      "Bash(git *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  },
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
          "patterns": ["DROP TABLE", "TRUNCATE", "rm -rf", "git push.*--force"]
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
          "prompt": "停止前自检：导出符号注释？错误处理？测试？格式？"
        }
      }
    ]
  }
}
```

---

## 九、搭建流程：从零到完整 Harness 的 6 步

### Step 1：创建 CLAUDE.md（30 分钟）

```bash
# 在项目根目录创建
touch CLAUDE.md
```

填写：项目概述 + 常用命令 + 架构概览 + 核心编码约定 + Git 规范

### Step 2：拆分 Rules（1-2 小时）

```bash
mkdir -p .claude/rules/
```

从项目现有的编码规范文档、Code Review 常见问题、CI 失败原因中提炼规范文件。优先级：
1. 错误处理规范
2. 日志规范
3. 项目结构/分层规范
4. 数据库规范

### Step 3：配置 Hooks（30 分钟）

```bash
mkdir -p .claude/hooks/
```

创建 `settings.json` + Hook 脚本。最小可行配置：
1. PostToolUse：自动格式化
2. PreToolUse：阻止危险操作

### Step 4：创建核心 Skills（1-2 天）

```bash
mkdir -p .claude/skills/review/
mkdir -p .claude/skills/gen-test/
```

优先创建 `/review`（代码审查）和 `/gen-test`（测试生成）。

### Step 5：验证与调优（持续）

- 试用每个 Skill，检查输出质量
- 观察 Hook 是否有误拦截
- 根据实际使用调整规范文件

### Step 6：团队推广

- 将配置提交到版本控制
- 在团队内分享使用方法
- 收集反馈持续迭代

---

## 十、度量与演进

### 10.1 Harness 成熟度模型

| 级别 | 名称 | 特征 |
|------|------|------|
| L0 | 裸奔 | 无 CLAUDE.md，无 rules，无 hooks |
| L1 | 有上下文 | 有 CLAUDE.md + 基础 rules |
| L2 | 有护栏 | L1 + Hooks（自动格式化、危险拦截） |
| L3 | 有能力 | L2 + 核心 Skills（审查、测试） |
| L4 | 全链路 | L3 + 工作流 Skills（脚手架、架构检查、部署） |
| L5 | 自演进 | L4 + 度量驱动的持续优化 |

### 10.2 度量指标

| 指标 | 说明 | 目标 |
|------|------|------|
| Hook 拦截率 | 被 Hook 拦截的违规操作占比 | 趋近 0（说明 Claude 已学会规范） |
| Skill 使用频率 | 每周各 Skill 被触发次数 | 稳定使用 |
| CI 通过率 | 首次提交的 CI 通过率 | >90% |
| Code Review 问题数 | 人工审查发现的规范问题 | 持续下降 |

---

## 附录 A：Skill 文件规范

### 文件结构

```
.claude/skills/{skill-name}/
├── SKILL.md                    # 必须：Skill 定义
├── references/                 # 可选：参考文档（Tier 3）
├── scripts/                    # 可选：辅助脚本（Tier 3）
└── templates/                  # 可选：代码模板（Tier 3）
```

### SKILL.md 必须字段

```yaml
---
name: kebab-case-name           # 必须
description: 一句话描述 + 触发词  # 必须
version: x.y.z                  # 推荐
---
```

### 命名规范

- Skill 名称：kebab-case，如 `code-review`、`gen-test`
- 文件名：全小写，SKILL.md 大写
- 触发词：放在 description 中，Claude 自动匹配

---

## 附录 B：Hook 脚本规范

### 输入

Hook 脚本通过环境变量或参数接收上下文：
- `$CLAUDE_FILE_PATH`：操作的文件路径
- `$1`：工具调用的参数

### 输出

JSON 格式输出到 stdout：

```json
{
  "decision": "approve|block|warn",
  "reason": "人可读的原因",
  "feedback": "给 Claude 的建议",
  "continue": true,
  "suppressOutput": false
}
```

### 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 通过 |
| 1 | 警告（不阻断） |
| 2 | 阻断 |

### 最佳实践

1. Hook 脚本必须快速执行（<2 秒），避免阻塞 Claude 工作
2. 阻断要给出清晰的修复建议（feedback 字段）
3. 优先用 `warn` 而非 `block`，除非是安全相关
4. Hook 脚本要处理好文件不存在等边界情况

---

## 附录 C：常见问题

### Q1：Rules 文件太多会不会浪费 token？

会。所有 `.claude/rules/` 下的文件会自动加载到上下文中。建议：
- 单个 rule 文件不超过 200 行
- 总规范不超过 20 个文件
- 详细内容放 Skill 的 references/ 下（按需加载）

### Q2：Hook 和 Pre-commit 有什么区别？

- **Pre-commit**：git 提交时触发，只检查已暂存的文件
- **Hook**：Claude 每次操作时触发，实时拦截/后处理

两者互补：Hook 在编码过程中实时护航，Pre-commit 在提交时最终把关。

### Q3：Skill 和 CLAUDE.md 里写的规范有什么区别？

- **CLAUDE.md / Rules**：始终在上下文中，告诉 Claude "规范是什么"
- **Skill**：按需加载，告诉 Claude "按什么流程执行"

例如：Rules 里写"日志必须用项目日志库"，Skill `/review` 里写"检查代码中是否使用了标准库 log"。

### Q4：如何调试 Hook 不生效？

1. 手动运行 Hook 脚本，检查输出和退出码
2. 检查 `settings.json` 的 JSON 语法是否正确
3. 检查 matcher 中的 tools 名称是否精确（大小写敏感）
4. 重启 Claude Code 会话

### Q5：Skill 没有被触发怎么办？

1. 检查 SKILL.md 是否在 `.claude/skills/{name}/` 目录下
2. 检查 frontmatter 中的 description 是否包含触发关键词
3. 重启 Claude Code 会话重新扫描 skills
4. 尝试直接用 `/skill-name` 命令触发
