#!/usr/bin/env bash
# POSIX-compliant wrapper for Antigravity Agent Core CLI
set -euo pipefail

if command -v python3 &>/dev/null; then
  python3 .agents/scripts/cli/helper.py "$@"
elif command -v python &>/dev/null; then
  python .agents/scripts/cli/helper.py "$@"
else
  echo "Error: Python 3 runtime is required to execute Antigravity CLI commands." >&2
  exit 1
fi
