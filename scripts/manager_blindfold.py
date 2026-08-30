import sys
import json
import os

def main():
    payload = sys.stdin.read()
    if not payload:
        return
        
    data = json.loads(payload)
    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    transcript_path = data.get("transcriptPath", "")
    
    # Only blindfold specific read tools
    if tool_name not in ["view_file", "grep_search", "list_dir", "find_by_name"]:
        print(json.dumps({"decision": "allow"}))
        return

    # Check if this agent is the Scrum Master by reading the first line of its transcript
    is_manager = False
    try:
        with open(transcript_path, 'r') as f:
            first_line = f.readline()
            if "Principal Agile Orchestrator" in first_line or "Scrum Master" in first_line:
                is_manager = True
    except Exception:
        pass
        
    if is_manager:
        target_path = ""
        if tool_name == "view_file":
            target_path = tool_args.get("AbsolutePath", "")
        elif tool_name == "grep_search":
            target_path = tool_args.get("SearchPath", "")
            
        # The Scrum Master is ONLY allowed to read the Blackboard (state.json)
        if "state.json" not in target_path and "inbox" not in target_path:
            print(json.dumps({
                "decision": "deny",
                "reason": "RBAC BLINDFOLD: As the Scrum Master, you are strictly forbidden from reading source code directly. You MUST spawn a sub-agent (e.g. staff-backend or devsecops-principal) to read and analyze these files for you, and coordinate with them via the Blackboard."
            }))
            return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
