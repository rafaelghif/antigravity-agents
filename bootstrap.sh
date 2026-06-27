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

# 2. Synchronize Version if AGENTS.md exists
if [ -f "AGENTS.md" ]; then
  if command -v python3 &>/dev/null; then
    python3 -c '
import re, os
with open("AGENTS.md", "r", encoding="utf-8") as f:
    content = f.read()
if "- **Version:**" in content:
    content = re.sub(r"-\s+\*\*Version:\*\*.*", "- **Version:** 2.26.0", content)
else:
    content = re.sub(r"(-\s+\*\*Product:\*\*.*)", r"\1\n- **Version:** 2.26.0", content)
with open("AGENTS.md", "w", encoding="utf-8") as f:
    f.write(content)
'
    echo "Synchronized AGENTS.md version."
  fi
fi

# 3. Trigger auto-reconnaissance if recon.py exists
if [ -f ".agents/scripts/recon.py" ]; then
  echo "Running enterprise auto-reconnaissance scan..."
  if command -v python3 &>/dev/null; then
    python3 .agents/scripts/recon.py
  else
    echo "Warning: python3 not found. Please run .agents/scripts/recon.py manually after installing python3."
  fi
else
  echo "Warning: .agents/scripts/recon.py not found. Skipping auto-reconnaissance."
fi

# 4. Set up local Git hooks
if [ -d ".git" ]; then
  # Pre-commit Hook
  cat << 'EOF' > .git/hooks/pre-commit
#!/usr/bin/env bash
if command -v python3 &>/dev/null; then
  python3 .agents/scripts/validate.py
else
  echo "Warning: python3 not found. Skipping commit validation check."
fi
EOF
  chmod +x .git/hooks/pre-commit
  echo "Installed local Git pre-commit hook."

  # Commit-msg Hook
  cat << 'EOF' > .git/hooks/commit-msg
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
  chmod +x .git/hooks/commit-msg
  echo "Installed local Git commit-msg hook."
fi

echo "=========================================================="
echo "   AAC V2 Bootstrap Completed Successfully!             "
echo "=========================================================="
