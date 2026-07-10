#!/usr/bin/env bash
# Environment bootstrap script for Antigravity Agent Core (AAC) V3
set -euo pipefail

echo "=========================================================="
echo "   Bootstrapping Antigravity Agent Core (AAC) V3...   "
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
import re, os, subprocess
def is_agent_core_repo():
    try:
        res = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True)
        if "antigravity-agents" in res.stdout.lower():
            return True
    except Exception:
        pass
    if os.path.exists("AGENTS.md"):
        try:
            with open("AGENTS.md", "r", encoding="utf-8") as f:
                content = f.read()
            product_match = re.search(r"-\s+\*\*Product:\*\*\s*(\S+)", content)
            if product_match and product_match.group(1) == "test-proj":
                return True
        except Exception:
            pass
    return False

if is_agent_core_repo():
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        content = f.read()
    if "- **Version:**" in content:
        content = re.sub(r"-\s+\*\*Version:\*\*.*", "- **Version:** 3.21.0", content)
    else:
        content = re.sub(r"(-\s+\*\*Product:\*\*.*)", r"\1\n- **Version:** 3.21.0", content)
    with open("AGENTS.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("Synchronized AGENTS.md version.")
'
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

# 4. Set up local Git hooks via validate.py
if git rev-parse --is-inside-work-tree &>/dev/null; then
  if [ -n "$PYTHON_EXEC" ]; then
    echo "Installing and validating local Git hooks..."
    "$PYTHON_EXEC" .agents/scripts/validate.py >/dev/null 2>&1 || true
    echo "Installed local Git hooks."
  else
    echo "Warning: Python 3 not found. Skipping Git hooks auto-installation."
  fi
fi

# 5. Run the python bootstrap setup wizard
if [ -n "$PYTHON_EXEC" ] && [ -f ".agents/scripts/cli/helper.py" ]; then
  echo "Running project setup wizard..."
  "$PYTHON_EXEC" .agents/scripts/cli/helper.py bootstrap "$@"
fi

echo "=========================================================="
echo "   AAC V3 Bootstrap Completed Successfully!             "
echo "=========================================================="
