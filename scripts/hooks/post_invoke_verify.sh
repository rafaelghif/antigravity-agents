#!/bin/bash

# Run verify.py and capture output to stderr or /dev/null so it doesn't pollute stdout JSON
if ! python3 scripts/verify.py > /dev/null 2>&1; then
    cat << 'INNER_EOF'
{
  "injectSteps": [{"ephemeralMessage": "CRITICAL: verify.py failed! You must fix the errors before completing the task."}],
  "terminationBehavior": "force_continue"
}
INNER_EOF
else
    echo "{}"
fi
