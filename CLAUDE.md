# 项目概览

这是一个用于沉淀后台开发 AI 编码助手使用最佳实践的知识库，专注于收集、整理和分享 AI 编码助手在实际开发中的使用经验、技巧和规范。

## 项目定位
- **文档型仓库**：主要包含 Markdown 文档，不涉及具体编程语言的代码开发
- **知识沉淀**：收集和整理 AI 编码助手在不同场景下的使用最佳实践
- **参考指南**：为后台开发同事使用 AI 编码助手提供实用的配置和使用建议

## 仓库结构
```
.
├── CLAUDE.md                              # 项目工作指南（本文件）
├── .claude/                               # Claude Code 配置目录
│   ├── commands/                          # 自动化命令
│   │   └── beego2gorm.md                # Beego ORM -> GORM 迁移工具（/beego2gorm 触发）
│   ├── rules/                             # 编码规范与规则
│   │   ├── golang_coding.md              # Go 语言编码规范
│   │   ├── mysql.md                      # MySQL 数据库设计规范
│   │   ├── gorm.md                       # GORM 使用规范
│   │   ├── pulsar.md                     # 消息队列 Pulsar 规范
│   │   ├── protobuf.md                   # Protobuf 接口定义规范
│   │   ├── log.md                        # 日志使用规范
│   │   ├── error.md                      # 错误处理规范
│   │   ├── comment.md                    # 代码注释规范
│   │   ├── redis.md                      # Redis 使用规范
│   │   ├── goroutine.md                  # Goroutine 使用规范
│   │   ├── id_generation.md              # 资源 ID 生成规范
│   │   └── project_structure.md          # 项目模块目录组织规范
│   └── skills/                            # 技能扩展
│       ├── beego2gorm/                   # Beego ORM -> GORM 迁移技能
│       │   └── SKILL.md
│       ├── backend-log-query/            # 后端日志查询技能
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── query_backend_log.py
│       └── frontend-log-query/           # 前端日志查询技能
│           ├── SKILL.md
│           └── scripts/
│               └── query_frontend_log.py
└── .gitignore
```

## Git 工作流程
- `main`: 主分支，保持稳定可用的文档
- `其他分支`: 新增、修正内容

## 重要提醒
**在编辑此仓库时，始终牢记**：
- 这是**知识沉淀库**，不是编程项目
- 内容要**准确、实用、清晰**
- 每个建议都应来自**真实使用经验**
- 避免添加**显而易见**或**过于通用**的内容
- 定期**审查和更新**过时的内容
- Agent/Command/Skill/Rule 配置应保持**单一职责**和**清晰边界**
