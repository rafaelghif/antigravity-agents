#!/bin/bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if ! (cd "$ROOT" && python3 scripts/verify.py --execute --terse > /dev/null 2>&1); then
    cat << 'INNER_EOF'
{
  "injectSteps": [{"ephemeralMessage": "CRITICAL: verify.py failed! You must fix the errors before completing the task."}],
  "terminationBehavior": "force_continue"
}
INNER_EOF
else
    echo "{}"
fi
