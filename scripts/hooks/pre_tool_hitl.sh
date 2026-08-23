#!/bin/bash
set -e

PAYLOAD=$(cat -)
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.toolCall.name // empty')

if [ "$TOOL_NAME" = "run_command" ]; then
    CMD=$(echo "$PAYLOAD" | jq -r '.toolCall.args.CommandLine // empty')
    
    if echo "$CMD" | grep -qE 'git push|docker push|npm publish'; then
        cat << 'INNER_EOF'
{
  "decision": "ask",
  "reason": "Production push detected. Human verification required."
}
INNER_EOF
        exit 0
    fi
fi

cat << 'INNER_EOF'
{
  "decision": "allow"
}
INNER_EOF
