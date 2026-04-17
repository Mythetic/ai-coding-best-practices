# AI Coding Best Practices

A knowledge base for accumulating best practices of using AI coding assistants (Claude Code, etc.) in backend development.

## What is This?

This repository is a **documentation-focused** project that collects, organizes, and shares practical experiences, tips, and standards for using AI coding assistants in real-world Go backend development.

## Repository Structure

```
.
├── CLAUDE.md                              # Project overview and guide
├── README.md                              # This file
├── docs/
│   └── harness-universal-guide.md         # Claude Code Harness universal methodology
├── .claude/                               # Claude Code configuration
│   ├── commands/                          # Custom slash commands
│   │   └── beego2gorm.md                 # Beego ORM → GORM migration command
│   ├── rules/                             # Coding standards & rules (12 files)
│   │   ├── golang_coding.md              # Go coding standards
│   │   ├── mysql.md                      # MySQL database design
│   │   ├── gorm.md                       # GORM usage standards
│   │   ├── error.md                      # Error handling standards
│   │   ├── log.md                        # Logging standards
│   │   ├── comment.md                    # Code comment standards
│   │   ├── protobuf.md                   # Protobuf definition standards
│   │   ├── pulsar.md                     # Message queue (Pulsar) standards
│   │   ├── redis.md                      # Redis usage standards
│   │   ├── goroutine.md                  # Goroutine best practices
│   │   ├── id_generation.md              # Resource ID generation
│   │   └── project_structure.md          # Project module organization
│   └── skills/                            # AI skill extensions
│       ├── harness-setup/                 # ★ One-click Harness configuration generator
│       ├── beego2gorm/                    # ORM migration skill
│       ├── backend-log-query/             # Backend log query skill
│       └── frontend-log-query/            # Frontend log query skill
└── .gitignore
```

## Key Features

### Harness Setup Skill (NEW)

**One-click Claude Code Harness configuration for any project.** Install this skill and run `/harness-setup` to automatically:

1. **Detect** your project's language, framework, architecture, and existing config
2. **Generate** CLAUDE.md with project overview, commands, and architecture
3. **Create** coding rules (`.claude/rules/`) extracted from your real codebase
4. **Configure** Hooks for auto-formatting and dangerous operation blocking
5. **Build** core Skills (`/review` for code review, `/gen-test` for test generation)

Supports: **Go, Python, TypeScript/JavaScript, Rust, Java**

Quick install:
```bash
# Copy to your project
cp -r .claude/skills/harness-setup /path/to/your/project/.claude/skills/

# Or install globally (available for all projects)
cp -r .claude/skills/harness-setup ~/.claude/skills/

# Then in Claude Code:
/harness-setup
```

See [harness-setup/README.md](.claude/skills/harness-setup/README.md) for full documentation.

### Harness Universal Guide

A **language-agnostic, framework-agnostic** methodology for building Claude Code Harness configurations. Covers:

- **Three-layer architecture**: Context (CLAUDE.md + Rules) → Automation (Hooks) → Capabilities (Skills)
- **6 reusable Skill patterns**: Code Review, Test Generation, CRUD Scaffold, Architecture Check, DB Review, i18n
- **5 reusable Hook patterns**: Auto-format, Dangerous Operation Blocking, File Size Limit, Secret Detection, Completion Check
- **Maturity model**: L0 (bare) → L5 (self-evolving)
- **Step-by-step setup flow**: From zero to full Harness in 6 steps

See [docs/harness-universal-guide.md](docs/harness-universal-guide.md) for the full guide.

### Rules (Coding Standards)
12 comprehensive coding rules covering every aspect of Go backend development:
- **Code Style**: Formatting, naming, import organization, magic numbers
- **Database**: MySQL design, GORM usage, sharding strategies
- **Error Handling**: Unified error library with error code management
- **Logging**: Structured logging with chain methods
- **Architecture**: Module organization, layered architecture (API → Logic → Repository)
- **Infrastructure**: Redis, Pulsar MQ, Protobuf, Goroutine safety
- **ID Generation**: Unified resource ID generation

### Commands
- `/beego2gorm` — Automated Beego ORM to GORM migration tool with comprehensive conversion rules

### Skills
- **harness-setup** — One-click Harness configuration generator (multi-language)
- **beego2gorm** — Interactive ORM migration assistant
- **backend-log-query** — Query backend logs via MCP platform
- **frontend-log-query** — Query frontend logs via MCP platform

## How to Use

### Quick Start: Harness Setup (Recommended)

1. Copy `.claude/skills/harness-setup/` to your project's `.claude/skills/`
2. Open Claude Code in your project
3. Run `/harness-setup`
4. Follow the guided 5-phase setup

### Manual Setup

1. Clone this repo
2. Copy the `.claude/` directory structure to your project
3. Customize the rules to match your project's specific conventions
4. Replace placeholder paths (e.g., `example.com/myproject/...`) with your actual import paths

## Rule Priority Levels

Each rule uses the following priority levels:
- **Mandatory**: Must follow, violations are errors
- **Preferable**: Should follow, exceptions allowed in special cases
- **Optional**: Reference material, adopt as applicable

## License

MIT
