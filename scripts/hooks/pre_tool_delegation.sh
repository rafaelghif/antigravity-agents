#!/bin/bash
# Pre-Tool Hook to enforce isolated per-file Micro-Task Agent-Optimized Prompting

payload=$(cat)
subagent_prompts=$(echo "$payload" | jq -r '.toolCall.args.Subagents[].Prompt')

# Ensure they are referencing isolated files in a tasks/ directory
if ! echo "$subagent_prompts" | grep -qE "tasks/[0-9a-zA-Z_]+\.yaml"; then
  cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL CONTEXT BLOAT PREVENTED: You must not bundle instructions. Split the task into small, isolated files inside a 'tasks/' directory (e.g., 'tasks/01_auth.yaml'). Your delegation prompt MUST explicitly reference the specific 'tasks/*.yaml' file the subagent should execute."
}
JSON_EOF
  exit 0
fi

# Allow execution
echo '{"decision": "allow"}'
