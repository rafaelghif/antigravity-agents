#!/usr/bin/env bash
# Thin POSIX-compliant bootstrapper delegate for Antigravity Agent Core (AAC) V3
set -euo pipefail

# 1. Prerequisite Check: Python 3 presence
PYTHON_EXEC=""
if command -v python3 &>/dev/null; then
  PYTHON_EXEC="python3"
elif command -v python &>/dev/null; then
  if python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_EXEC="python"
  fi
fi

if [ -z "$PYTHON_EXEC" ]; then
  echo "Error: Python 3 runtime is required to execute bootstrap." >&2
  exit 1
fi

# 2. Delegate directly to the Python bootstrap command
"$PYTHON_EXEC" .agents/scripts/cli/helper.py bootstrap "$@"
