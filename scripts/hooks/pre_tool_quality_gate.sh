#!/bin/bash
# Strict Quality Gate for Code Implementation

payload=$(cat)
tool_name=$(echo "$payload" | jq -r '.toolCall.name')

if [[ "$tool_name" == "write_to_file" || "$tool_name" == "replace_file_content" ]]; then
  
  # 1. Check if this is writing a task definition. If so, allow it.
  target_file=$(echo "$payload" | jq -r '.toolCall.args.TargetFile')
  if echo "$target_file" | grep -qE "tasks/.*\.yaml$"; then
    echo '{"decision": "allow"}'
    exit 0
  fi

  # 2. If it's writing code but tasks/ doesn't exist, enforce /grill-me and micro-tasks
  if [ ! -d "tasks" ]; then
    cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL PROTOCOL VIOLATION: You bypassed the /grill-me phase! You are STRICTLY FORBIDDEN from writing code before gathering requirements. You MUST initiate the /grill-me interactive interview using ask_question to align on requirements. Then, you MUST split the architecture into atomic micro-tasks and save them inside the 'tasks/' directory (e.g., tasks/01_auth.yaml). DO NOT write source code yet."
}
JSON_EOF
    exit 0
  fi

  # 3. Check if the description includes algorithmic and DB scalability justification
  desc=$(echo "$payload" | jq -r '.toolCall.args.Description // .toolCall.args.Instruction')
  if ! echo "$desc" | grep -qiE "complexity|O\(|index|cache|scaling|N\+1"; then
    cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL ENTERPRISE REJECTION: You are bypassing L9 scaling standards! Your tool Description/Instruction MUST explicitly state the Time/Space Complexity (e.g., O(1), O(log N)) AND Database Scaling strategy (e.g., prevents N+1, uses Indexes, Caching). Re-evaluate your code, ensure it is horizontally scalable, and call the tool again with a proper engineering justification."
}
JSON_EOF
    exit 0
  fi
fi

# Allow execution
echo '{"decision": "allow"}'
