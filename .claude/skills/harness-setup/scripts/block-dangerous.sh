#!/bin/bash
#
# block-dangerous.sh — PreToolUse Hook 模板
# 拦截 Claude 执行的危险操作
#
# 使用方式：
# 1. 复制到 .claude/hooks/ 目录
# 2. 根据项目需要调整拦截规则
# 3. chmod +x .claude/hooks/block-dangerous.sh
#

INPUT="$1"

# ============================================================
# 1. 数据库危险操作
# ============================================================

# 禁止物理删除表
if echo "$INPUT" | grep -iE "DROP\s+TABLE|TRUNCATE\s+TABLE" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"禁止 DROP TABLE / TRUNCATE TABLE 操作","feedback":"如需废弃表请使用 RENAME TABLE xxx TO xxx_drop","continue":false}
EOF
  exit 2
fi

# 禁止无条件 DELETE
if echo "$INPUT" | grep -iE "DELETE\s+FROM\s+\w+\s*$" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"禁止无条件 DELETE FROM（缺少 WHERE 子句）","feedback":"请添加 WHERE 条件，或使用软删除","continue":false}
EOF
  exit 2
fi

# ============================================================
# 2. Git 危险操作
# ============================================================

# 禁止 force push
if echo "$INPUT" | grep -E "git\s+push\s+.*--force[^-]|git\s+push\s+.*-f\b" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"禁止 force push","feedback":"请使用 --force-with-lease 或正常推送","continue":false}
EOF
  exit 2
fi

# 禁止 force push 到 main/master
if echo "$INPUT" | grep -E "git\s+push\s+.*\s+(main|master)\s+--force|git\s+push\s+--force\s+.*\s+(main|master)" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"严禁 force push 到 main/master 分支","continue":false}
EOF
  exit 2
fi

# ============================================================
# 3. 文件系统危险操作
# ============================================================

# 禁止删除根目录
if echo "$INPUT" | grep -E "rm\s+-rf\s+/\s|rm\s+-rf\s+/\$" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"禁止删除根目录","continue":false}
EOF
  exit 2
fi

# 警告大范围删除
if echo "$INPUT" | grep -E "rm\s+-rf\s+" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"warn","reason":"检测到 rm -rf 操作，请确认删除范围","feedback":"建议先 ls 查看目录内容再删除"}
EOF
  exit 1
fi

# ============================================================
# 4. 环境危险操作
# ============================================================

# 禁止 sudo
if echo "$INPUT" | grep -E "^\s*sudo\s+" > /dev/null 2>&1; then
  cat <<'EOF'
{"decision":"block","reason":"禁止使用 sudo","feedback":"请在非特权模式下操作","continue":false}
EOF
  exit 2
fi

# ============================================================
# 通过
# ============================================================
echo '{"decision":"approve"}'
exit 0
