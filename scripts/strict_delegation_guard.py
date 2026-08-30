import sys
import json
import os

def main():
    payload = sys.stdin.read()
    if not payload:
        return
        
    data = json.loads(payload)
    tool_args = data.get("toolCall", {}).get("args", {})
    target_file = tool_args.get("TargetFile", "")
    
    # We allow the Primary Agent to modify framework files (.md docs, config, scripts)
    # But we FORBID it from touching application code (e.g., src/, tests/, app/)
    forbidden_dirs = ["/src/", "/app/", "/tests/", "/lib/"]
    
    is_forbidden = any(fd in target_file for fd in forbidden_dirs)
    
    if is_forbidden:
        print(json.dumps({
            "decision": "deny",
            "reason": "STRICT_DELEGATION Rule Violated: The Primary Agent is a Meta-Router and cannot modify application code directly. You MUST delegate to an L9 Sub-agent via invoke_subagent."
        }))
    else:
        print(json.dumps({
            "decision": "allow"
        }))

if __name__ == "__main__":
    main()
