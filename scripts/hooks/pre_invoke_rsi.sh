#!/bin/bash

# Read the JSON payload
payload=$(cat)

# Extract transcript path
transcript_path=$(echo "$payload" | jq -r '.transcriptPath')

# We only care if we have a transcript
if [ -f "$transcript_path" ]; then
    # Get the last tool call execution result
    last_step=$(tail -n 1 "$transcript_path")
    
    # Check if the last step was a TOOL_RESPONSE indicating a failure for run_command
    # We can check if it contains "exit code 1" or "failed" or if the step status is ERROR
    # Actually, run_command returns the output. If the output contains "ERROR:" or "failed with exit code", it's a failure.
    if echo "$last_step" | grep -qiE "failed with exit code|error:|exception:|traceback|exit status"; then
        # Check if it was a run_command response
        # In the transcript, tool responses usually have "type":"TOOL_RESPONSE"
        if echo "$last_step" | grep -q '"type":"TOOL_RESPONSE"'; then
            cat << 'JSON_EOF'
{
  "injectSteps": [
    {
      "ephemeralMessage": "🚨 RSI PROTOCOL TRIGGERED 🚨: The previous terminal command failed! DO NOT guess the solution. You MUST immediately call `invoke_subagent` to spawn a `reviewer` subagent. Give the reviewer the error logs and ask it to analyze the root cause and provide a patch."
    }
  ]
}
JSON_EOF
            exit 0
        fi
    fi
fi

# Default: do nothing
echo '{}'
