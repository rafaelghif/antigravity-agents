#!/usr/bin/env bash
# Thin POSIX-compliant bootstrapper delegate for Antigravity Agent Core (AAC) V3
set -euo pipefail

# 1. Prerequisite Check: Check if standalone binary exists
OS="$(uname -s)"
ARCH="$(uname -m)"
BINARY_NAME="agy-${OS}-${ARCH}"
if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    BINARY_NAME="agy-Windows-${ARCH}.exe"
fi

# Try local bin first, then global install bin
if [ -x "bin/${BINARY_NAME}" ]; then
  exec "bin/${BINARY_NAME}" bootstrap "$@"
elif [ -x "$HOME/.local/bin/${BINARY_NAME}" ]; then
  exec "$HOME/.local/bin/${BINARY_NAME}" bootstrap "$@"
fi

# 2. Prerequisite Check: Python 3 fallback
PYTHON_EXEC=""
if command -v python3 &>/dev/null; then
  PYTHON_EXEC="python3"
elif command -v python &>/dev/null; then
  if python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_EXEC="python"
  fi
fi

if [ -z "$PYTHON_EXEC" ]; then
  echo "Error: Standalone binary not found and Python 3 runtime is missing." >&2
  echo "Please download the compiled binary from GitHub Releases or install Python 3.8+." >&2
  exit 1
fi

# 3. Delegate to the Python bootstrap command
"$PYTHON_EXEC" .agents/scripts/cli/helper.py bootstrap "$@"
