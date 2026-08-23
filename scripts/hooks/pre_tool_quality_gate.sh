#!/bin/bash
# Strict Quality Gate for Code Implementation (TDD + Scalability)

payload=$(cat)
tool_name=$(echo "$payload" | jq -r '.toolCall.name')

if [[ "$tool_name" == "write_to_file" || "$tool_name" == "replace_file_content" ]]; then
  
  target_file=$(echo "$payload" | jq -r '.toolCall.args.TargetFile')

  # 1. Allow tasks/*.yaml without grill check (it's the grill output)
  if echo "$target_file" | grep -qE "tasks/.*\.yaml$"; then
    echo '{"decision": "allow"}'
    exit 0
  fi

  # 2. Enforce /grill-me and micro-tasks existence
  if [ ! -d "tasks" ]; then
    cat << 'JSON_EOF'
{
  "decision": "ask",
  "reason": "CRITICAL PROTOCOL VIOLATION: You bypassed the /grill-me phase! You are STRICTLY FORBIDDEN from writing code before gathering requirements. You MUST initiate the /grill-me interactive interview using ask_question to align on requirements. Then, you MUST split the architecture into atomic micro-tasks and save them inside the 'tasks/' directory (e.g., tasks/01_auth.yaml). DO NOT write source code yet."
}
JSON_EOF
    exit 0
  fi

  # 3. Mandatory TDD Gate: If writing source code, ensure a test file exists first!
  # Let's say any .py file outside /tests/ or /scripts/ needs a test file
  if echo "$target_file" | grep -qE "\.py$|\.ts$|\.js$"; then
    # Ignore if we are writing a test file itself or scripts/ config files
    if ! echo "$target_file" | grep -qE "test_|spec\.|\.test\.|tests/|scripts/|\.agents/|setup\.py"; then
      basename=$(basename "$target_file")
      name_without_ext="${basename%.*}"
      ext="${basename##*.}"
      
      # We check if a test file exists somewhere in the workspace
      # e.g., test_auth.py or auth.test.ts
      test_exists=$(find . -type f -name "test_${name_without_ext}.${ext}" -o -name "${name_without_ext}.test.${ext}" -o -name "${name_without_ext}.spec.${ext}" 2>/dev/null | head -n 1)
      
      if [ -z "$test_exists" ]; then
        cat << JSON_EOF
{
  "decision": "ask",
  "reason": "TDD VIOLATION: You are attempting to write source code ('$basename') BEFORE writing its test file! World-class Agentic Standard mandates Test-Driven Development (TDD). You MUST write the test file (e.g., 'test_$basename' or '${name_without_ext}.test.${ext}') FIRST, before you are allowed to modify the implementation."
}
JSON_EOF
        exit 0
      fi
    fi
  fi

  # 4. Enforce Algorithmic and DB scalability justification
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
