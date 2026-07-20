#!/usr/bin/env bash
# POSIX-compliant wrapper for Antigravity Agent Core CLI
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "[AAC HALT] CRITICAL ERROR: Python 3 runtime is required but not found on this system!" >&2
  echo "[AAC HALT] The agent MUST HALT execution immediately and inform the human to install Python 3." >&2
  exit 1
fi

if ! "$PYTHON_CMD" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' &>/dev/null; then
  echo "[AAC HALT] CRITICAL ERROR: Python 3.8+ is required. Found: $("$PYTHON_CMD" --version)" >&2
  echo "[AAC HALT] The agent MUST HALT execution immediately and inform the human to upgrade Python." >&2
  exit 1
fi

"$PYTHON_CMD" "$SCRIPT_DIR/.agents/scripts/cli/helper.py" "$@"
