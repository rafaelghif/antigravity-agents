#!/bin/bash
set -e

PAYLOAD=$(cat -)
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.toolCall.name // empty')

if [ "$TOOL_NAME" = "run_command" ]; then
    CMD=$(echo "$PAYLOAD" | jq -r '.toolCall.args.CommandLine // empty')
    
    if echo "$CMD" | grep -qE 'git push|docker push|npm publish'; then
        
        # Multi-Agent Consensus Check (AITL)
        if [ ! -f ".agents/brain/AITL_CONSENSUS.yaml" ]; then
            cat << 'INNER_EOF'
{
  "decision": "ask",
  "reason": "PRODUCTION GATE BLOCKED: No Human-in-the-Loop (HITL) OR Agent-in-the-Loop (AITL) consensus found. To deploy autonomously, you MUST invoke the 'reviewer' and 'security-reviewer' subagents and save their approval to '.agents/brain/AITL_CONSENSUS.yaml'."
}
INNER_EOF
            exit 0
        fi

        # If consensus exists, we still force a human ask, or we can allow it!
        # The user wanted AITL: "Menolak perintah git commit/push kecuali jika agen reviewer..."
        # If AITL_CONSENSUS.yaml exists, we check if it contains APPROVED
        if ! grep -q "STATUS: APPROVED" ".agents/brain/AITL_CONSENSUS.yaml"; then
            cat << 'INNER_EOF'
{
  "decision": "ask",
  "reason": "PRODUCTION GATE BLOCKED: The AITL_CONSENSUS.yaml file exists but lacks 'STATUS: APPROVED'. The peer agents did not approve this deployment."
}
INNER_EOF
            exit 0
        fi
        
        # If AITL approved, we can allow the push autonomously!
        cat << 'INNER_EOF'
{
  "decision": "allow",
  "reason": "AITL Consensus verified. Deployment authorized."
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
