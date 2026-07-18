#!/usr/bin/env bash
# Thin POSIX-compliant installer delegate for Antigravity Agent Core (AAC) V3
set -euo pipefail

TARGET_DIR="${1:-.}"
shift 2>/dev/null || true

# 1. Prerequisite Check: Git presence
if ! command -v git &>/dev/null; then
  echo "Error: Git is required to download/install Antigravity Agent Core." >&2
  exit 1
fi

# 2. Clone source repository to a temp directory
REPO_URL="${AAC_SOURCE_REPO:-https://github.com/rafaelghif/antigravity-agents.git}"
IS_ONLINE=0
for PROTO in "http://" "https://" "git@" "ssh://"; do
  if [[ "$REPO_URL" == "$PROTO"* ]]; then
    IS_ONLINE=1
    break
  fi
done
if [ "$IS_ONLINE" -eq 0 ]; then
  REPO_URL="https://github.com/rafaelghif/antigravity-agents.git"
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR" >/dev/null 2>&1 || true' EXIT

echo "Fetching latest source core files..."
if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" &>/dev/null; then
  echo "Error: Failed to clone source repository from $REPO_URL." >&2
  exit 1
fi

# 3. Prerequisite Check: Python 3 presence and minimum version >= 3.8
PYTHON_EXEC=""
if command -v python3 &>/dev/null; then
  PYTHON_EXEC="python3"
elif command -v python &>/dev/null; then
  if python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_EXEC="python"
  fi
fi

if [ -z "$PYTHON_EXEC" ]; then
  echo "Error: Python 3.8+ is required to run Antigravity Agent Core." >&2
  exit 1
fi

# Check version
PYTHON_VERSION=$("$PYTHON_EXEC" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]; }; then
  echo "Error: Python 3.8 or newer is required. Found Python $PYTHON_VERSION." >&2
  exit 1
fi

# 4. Invoke the python unified installer from the cloned temp repository
"$PYTHON_EXEC" "$TEMP_DIR/repo/.agents/scripts/cli/helper.py" install "$TARGET_DIR" "$@"
