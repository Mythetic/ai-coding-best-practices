#!/bin/bash
#
# auto-format.sh — PostToolUse Hook 模板
# Claude 编辑文件后自动执行格式化
#
# 使用方式：
# 1. 复制到 .claude/hooks/ 目录
# 2. 根据项目语言修改格式化命令
# 3. chmod +x .claude/hooks/auto-format.sh
#

FILE="$CLAUDE_FILE_PATH"

# 如果文件不存在（已删除），直接通过
if [ ! -f "$FILE" ]; then
  echo '{"decision":"approve"}'
  exit 0
fi

case "$FILE" in
  # Go 项目
  *.go)
    if command -v goimports &>/dev/null; then
      goimports -w "$FILE" 2>/dev/null
    elif command -v gofmt &>/dev/null; then
      gofmt -w "$FILE" 2>/dev/null
    fi
    ;;

  # Python 项目
  *.py)
    if command -v black &>/dev/null; then
      black --quiet "$FILE" 2>/dev/null
    elif command -v ruff &>/dev/null; then
      ruff format "$FILE" 2>/dev/null
    fi
    ;;

  # JavaScript / TypeScript 项目
  *.js|*.jsx|*.ts|*.tsx)
    if command -v prettier &>/dev/null; then
      prettier --write "$FILE" 2>/dev/null
    fi
    ;;

  # Rust 项目
  *.rs)
    if command -v rustfmt &>/dev/null; then
      rustfmt "$FILE" 2>/dev/null
    fi
    ;;

  # Java 项目
  *.java)
    if command -v google-java-format &>/dev/null; then
      google-java-format -i "$FILE" 2>/dev/null
    fi
    ;;
esac

echo '{"decision":"approve"}'
exit 0
