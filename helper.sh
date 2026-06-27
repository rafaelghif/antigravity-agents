#!/usr/bin/env bash
# POSIX-compliant wrapper for Antigravity Agent Core CLI
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if command -v python3 &>/dev/null; then
  python3 "$SCRIPT_DIR/.agents/scripts/cli/helper.py" "$@"
elif command -v python &>/dev/null; then
  python "$SCRIPT_DIR/.agents/scripts/cli/helper.py" "$@"
else
  echo "Error: Python 3 runtime is required to execute Antigravity CLI commands." >&2
  exit 1
fi
