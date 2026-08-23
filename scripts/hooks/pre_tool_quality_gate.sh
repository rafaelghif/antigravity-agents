#!/bin/bash
# Strict Quality Gate for Code Implementation

payload=$(cat)
tool_name=$(echo "$payload" | jq -r '.toolCall.name')

if [[ "$tool_name" == "write_to_file" || "$tool_name" == "replace_file_content" ]]; then
  desc=$(echo "$payload" | jq -r '.toolCall.args.Description // .toolCall.args.Instruction')
  
  # Check if the description includes algorithmic and DB scalability justification
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
