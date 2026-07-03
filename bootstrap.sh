#!/usr/bin/env bash
# Environment bootstrap script for Antigravity Agent Core (AAC) V2
set -euo pipefail

echo "=========================================================="
echo "   Bootstrapping Antigravity Agent Core (AAC) V2...   "
echo "=========================================================="

# 1. Create directories
mkdir -p .agents/memory/decisions
mkdir -p .agents/tasks
mkdir -p .agents/issues

# 1.1 Copy template memory files
if [ -d ".agents/memory/templates" ]; then
  for t in ".agents/memory/templates/"*.template; do
    [ -f "$t" ] || continue
    filename_t=$(basename "$t" .template)
    cp -n "$t" ".agents/memory/$filename_t" 2>/dev/null || true
  done
fi

# 1.2 Detect Python 3 executable
PYTHON_EXEC=""
if command -v python3 &>/dev/null; then
  PYTHON_EXEC="python3"
elif command -v python &>/dev/null; then
  if python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_EXEC="python"
  fi
fi

# 2. Synchronize Version if AGENTS.md exists
if [ -f "AGENTS.md" ] && [ -n "$PYTHON_EXEC" ]; then
  "$PYTHON_EXEC" -c '
import re, os
with open("AGENTS.md", "r", encoding="utf-8") as f:
    content = f.read()
if "- **Version:**" in content:
    content = re.sub(r"-\s+\*\*Version:\*\*.*", "- **Version:** 2.121.0", content)
else:
    content = re.sub(r"(-\s+\*\*Product:\*\*.*)", r"\1\n- **Version:** 2.121.0", content)
with open("AGENTS.md", "w", encoding="utf-8") as f:
    f.write(content)
'
  echo "Synchronized AGENTS.md version."
fi

# 3. Trigger auto-reconnaissance if recon.py exists
if [ -f ".agents/scripts/recon.py" ]; then
  echo "Running enterprise auto-reconnaissance scan..."
  if [ -n "$PYTHON_EXEC" ]; then
    "$PYTHON_EXEC" .agents/scripts/recon.py
  else
    echo "Warning: Python 3 not found. Please run .agents/scripts/recon.py manually after installing Python 3."
  fi
else
  echo "Warning: .agents/scripts/recon.py not found. Skipping auto-reconnaissance."
fi

# 4. Set up local Git hooks
if git rev-parse --is-inside-work-tree &>/dev/null; then
  HOOKS_DIR=$(git rev-parse --git-path hooks)
  PREFIX=$(git rev-parse --show-prefix)
  mkdir -p "$HOOKS_DIR"

  # Pre-commit Hook
  cat << EOF > "$HOOKS_DIR/pre-commit"
#!/usr/bin/env bash
if command -v python3 &>/dev/null; then
  python3 "${PREFIX}.agents/scripts/validate.py"
elif command -v python &>/dev/null; then
  python "${PREFIX}.agents/scripts/validate.py"
else
  echo "Warning: Python not found. Skipping commit validation check."
fi
EOF
  chmod +x "$HOOKS_DIR/pre-commit"
  echo "Installed local Git pre-commit hook."

  # Commit-msg Hook
  cat << 'EOF' > "$HOOKS_DIR/commit-msg"
#!/usr/bin/env bash
COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
CONVENTIONAL_REGEX="^(feat|fix|chore|refactor|docs|test|style|perf|ci)(\([a-z0-9_-]+\))?: .+"

if [[ ! "$COMMIT_MSG" =~ $CONVENTIONAL_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Non-compliant commit message format!"
  echo "=========================================================="
  echo "Commit messages must follow Conventional Commits standard:"
  echo "  Format: <type>(<scope>): <subject>"
  echo "  Example: feat(auth): add login endpoint"
  echo "=========================================================="
  exit 1
fi

ID_REGEX="(task-|issue-|chore-)[a-zA-Z0-9_-]+"
if [[ ! "$COMMIT_MSG" =~ $ID_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Missing Task/Issue ID reference!"
  echo "=========================================================="
  echo "Commit messages must include an active task or issue ID reference."
  echo "  Example body: Task ID: issue-123"
  echo "=========================================================="
  exit 1
fi
EOF
  chmod +x "$HOOKS_DIR/commit-msg"
  echo "Installed local Git commit-msg hook."

  # Prepare-commit-msg Hook
  cat << EOF > "$HOOKS_DIR/prepare-commit-msg"
#!/usr/bin/env bash
COMMIT_MSG_FILE="\$1"
COMMIT_SOURCE="\${2:-}"

if command -v python3 &>/dev/null; then
  python3 "${PREFIX}.agents/scripts/prepare_commit_msg.py" "\$COMMIT_MSG_FILE" "\$COMMIT_SOURCE"
elif command -v python &>/dev/null; then
  python "${PREFIX}.agents/scripts/prepare_commit_msg.py" "\$COMMIT_MSG_FILE" "\$COMMIT_SOURCE"
fi
EOF
  chmod +x "$HOOKS_DIR/prepare-commit-msg"
  echo "Installed local Git prepare-commit-msg hook."
fi

echo "=========================================================="
echo "   AAC V2 Bootstrap Completed Successfully!             "
echo "=========================================================="
