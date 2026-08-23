#!/bin/bash
# Pre-Tool Hook to enforce isolated per-file Micro-Task Agent-Optimized Prompting

payload=$(cat)
subagent_prompts=$(echo "$payload" | jq -r '.toolCall.args.Subagents[].Prompt')

# 1. Check if the prompt references a tasks/*.yaml file
if ! echo "$subagent_prompts" | grep -qE "tasks/[0-9a-zA-Z_]+\.yaml"; then
  cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL CONTEXT BLOAT PREVENTED: You must not bundle instructions. Split the task into small, isolated files inside a 'tasks/' directory (e.g., 'tasks/01_auth.yaml'). Your delegation prompt MUST explicitly reference the specific 'tasks/*.yaml' file the subagent should execute."
}
JSON_EOF
  exit 0
fi

# 2. Extract the referenced yaml file
task_file=$(echo "$subagent_prompts" | grep -oE "tasks/[0-9a-zA-Z_]+\.yaml" | head -n 1)

# 3. Check if the tasks directory and the referenced file actually exist
if [ ! -d "tasks" ] || [ ! -f "$task_file" ]; then
  cat << JSON_EOF
{
  "decision": "ask",
  "reason": "PHYSICAL VERIFICATION FAILED: You referenced '$task_file', but it does not exist on disk! You MUST use write_to_file to physically create the 'tasks/' directory and generate the atomic micro-task YAML files before delegating."
}
JSON_EOF
  exit 0
fi

# Allow execution
echo '{"decision": "allow"}'
