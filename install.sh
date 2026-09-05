#!/bin/sh
# Antigravity Agent Core (AAC) Universal POSIX Bootstrap
# Delegates installation to cross-platform pure Python engine (install.py)
# Version marker for validation:  AAC_REF="v4.46.0"

set -e

export PYTHONIOENCODING="utf-8"
export PYTHONUTF8="1"

PYTHON=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "Error: Python 3 is required to install Antigravity Agent Core." >&2
  exit 1
fi

SCRIPT_DIR="$(dirname "$0" 2>/dev/null || echo ".")"
if [ -f "$SCRIPT_DIR/install.py" ]; then
  exec "$PYTHON" "$SCRIPT_DIR/install.py" "$@"
fi

TMP_PY="$(mktemp "${TMPDIR:-/tmp}/aac_install_XXXXXX.py" 2>/dev/null || echo "/tmp/aac_install_$$.py")"
URL="https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.py"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP_PY"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP_PY" "$URL"
else
  echo "Error: curl or wget is required to download installer." >&2
  exit 1
fi

"$PYTHON" "$TMP_PY" "$@"
ret=$?
rm -f "$TMP_PY"
exit $ret
