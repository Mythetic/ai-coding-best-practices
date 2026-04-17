# AI Coding Best Practices

A knowledge base for accumulating best practices of using AI coding assistants (Claude Code, etc.) in backend development.

## What is This?

This repository is a **documentation-focused** project that collects, organizes, and shares practical experiences, tips, and standards for using AI coding assistants in real-world Go backend development.

## Repository Structure

```
.
├── CLAUDE.md                              # Project overview and guide
├── README.md                              # This file
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
│       ├── beego2gorm/                    # ORM migration skill
│       ├── backend-log-query/             # Backend log query skill
│       └── frontend-log-query/            # Frontend log query skill
└── .gitignore
```

## Key Features

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
- **beego2gorm** — Interactive ORM migration assistant
- **backend-log-query** — Query backend logs via MCP platform
- **frontend-log-query** — Query frontend logs via MCP platform

## How to Use

1. Clone this repo
2. Copy the `.claude/` directory structure to your project
3. Customize the rules to match your project's specific conventions
4. Replace placeholder paths (e.g., `example.com/myproject/...`) with your actual import paths

## Rule Priority Levels

Each rule uses the following priority levels:
- **Mandatory (必须)**: Must follow, violations are errors
- **Preferable (推荐)**: Should follow, exceptions allowed in special cases
- **Optional (可选)**: Reference material, adopt as applicable

## License

MIT
