# Harness Setup Skill — 安装指南

## 快速安装

从 GitHub 仓库获取并复制到目标项目即可。

### 方式一：从 GitHub 克隆后复制

```bash
git clone https://github.com/Mythetic/ai-coding-best-practices.git /tmp/ai-coding-best-practices

# 复制到目标项目
cp -r /tmp/ai-coding-best-practices/.claude/skills/harness-setup /path/to/your/project/.claude/skills/
```

### 方式二：全局安装（所有项目可用）

```bash
git clone https://github.com/Mythetic/ai-coding-best-practices.git /tmp/ai-coding-best-practices

# 安装到全局 skills 目录
cp -r /tmp/ai-coding-best-practices/.claude/skills/harness-setup ~/.claude/skills/
```

## 安装后的目录结构

```
.claude/skills/harness-setup/
├── SKILL.md                     # Skill 定义文件（必须）
├── references/
│   └── language-patterns.md     # 各语言规范模板参考
├── scripts/
│   ├── auto-format.sh           # 自动格式化 Hook 脚本模板
│   └── block-dangerous.sh       # 危险操作拦截 Hook 脚本模板
└── README.md                    # 本文件
```

## 使用方式

安装完成后，在 Claude Code 中使用以下任一方式触发：

```
/harness-setup
搭建 harness
配置 harness
帮项目配 Claude
初始化 Claude Code 配置
```

Skill 会自动执行以下流程：

1. **Phase 0**: 项目探测（语言、框架、架构、已有配置）
2. **Phase 1**: 生成/补充 CLAUDE.md
3. **Phase 2**: 生成编码规范 Rules
4. **Phase 3**: 配置自动化 Hooks
5. **Phase 4**: 创建核心 Skills（/review、/gen-test）
6. **Phase 5**: 输出总结报告

每个阶段完成后会暂停等待确认，你可以随时调整方案。

## 支持的语言/框架

| 语言 | 格式化 | 测试 | 状态 |
|------|--------|------|------|
| Go | goimports / gofmt | go test | ✅ 完整支持 |
| Python | black / ruff | pytest | ✅ 完整支持 |
| TypeScript/JavaScript | prettier | jest / vitest | ✅ 完整支持 |
| Rust | rustfmt | cargo test | ✅ 完整支持 |
| Java | google-java-format | maven/gradle test | ✅ 完整支持 |

## 常见问题

### Q: 已有部分配置，会覆盖吗？

不会。Skill 会先检测已有配置，只增量补充缺失部分。如果项目已有完整 Harness，会输出差距分析报告。

### Q: 可以只执行某个阶段吗？

可以。在 Phase 0 的确认步骤中，取消不需要的配置项即可跳过对应阶段。

### Q: 生成的规范不适合我的项目怎么办？

Skill 在每个阶段都会暂停等待确认。你可以要求修改后再写入，也可以后续手动调整 `.claude/rules/` 下的文件。

### Q: Hook 脚本需要安装额外工具吗？

格式化 Hook 会自动检测已安装的格式化工具（如 goimports、black、prettier）。如果工具不存在，会静默跳过。
