#!/bin/bash
# Pre-Tool Hook to enforce Agent-Optimized Prompting for invoke_subagent

payload=$(cat)
subagent_prompts=$(echo "$payload" | jq -r '.toolCall.args.Subagents[].Prompt')

# Check if the prompt contains XML tags or YAML indicators like <directive> or <context>
if ! echo "$subagent_prompts" | grep -qE "<directive>|<context>|<constraints>|task_breakdown.yaml"; then
  cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL: Subagent prompts must use Agent-Optimized Prompting! Your prompt lacks structural tags like <directive>, <context>, or <constraints>. Reformat the task using task_breakdown.yaml before delegating."
}
JSON_EOF
  exit 0
fi

# Allow execution
echo '{"decision": "allow"}'
