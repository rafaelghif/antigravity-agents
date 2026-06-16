#!/usr/bin/env bash

# Check for Python 3
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1 && [ "$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)" = "3" ]; then
    PY_CMD="python"
else
    echo "Error: Python 3 is required to run the Antigravity helper CLI." >&2
    echo "Please install Python 3 and ensure it is in your PATH." >&2
    exit 1
fi

"$PY_CMD" "$(dirname "${BASH_SOURCE[0]}")/cli/helper.py" "$@"
