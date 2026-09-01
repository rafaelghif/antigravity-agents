import sys
import json
import os
import subprocess
import glob
import time
import re

def log_to_blackboard(msg):
    try:
        subprocess.run(["python3", "scripts/inbox_manager.py", "send", "manager_blindfold", "all", msg], check=True)
    except Exception as e:
        sys.stderr.write(f"Blindfold log error: {e}\n")

def kill_rogue_processes():
    cmd = "ps -eo pid,etimes,cmd | grep cortex | grep -v grep"
    try:
        output = subprocess.check_output(cmd, shell=True).decode()
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            pid = int(parts[0])
            etimes = int(parts[1])
            if etimes > 900:
                os.kill(pid, 9)
                log_to_blackboard(f"Enforcement: Killed rogue agent PID {pid} (exceeded time limit of 900s)")
    except Exception as e:
        sys.stderr.write(f"Process check notice: {e}\n")

def reset_stuck_tasks():
    for task_file in glob.glob("tasks/*.yaml"):
        try:
            mtime = os.path.getmtime(task_file)
            if time.time() - mtime > 900:
                with open(task_file, "r") as f:
                    content = f.read()
                if 'status: "IN_PROGRESS"' in content:
                    content = re.sub(r'status:\s*"IN_PROGRESS"', 'status: "PENDING"', content)
                    with open(task_file, "w") as f:
                        f.write(content)
                    log_to_blackboard(f"Enforcement: Reset stuck task {task_file} to PENDING due to timeout")
        except Exception as e:
            sys.stderr.write(f"Task check notice: {e}\n")

def enforce_timeouts():
    kill_rogue_processes()
    reset_stuck_tasks()

def check_is_manager(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return False
    try:
        with open(transcript_path, 'r') as f:
            first_line = f.readline()
            return "Principal Agile Orchestrator" in first_line or "Scrum Master" in first_line
    except Exception as e:
        sys.stderr.write(f"Transcript read notice: {e}\n")
        return False

def main():
    payload = sys.stdin.read()
    if not payload:
        return
        
    data = json.loads(payload)
    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    transcript_path = data.get("transcriptPath", "")

    enforce_timeouts()
    is_manager = check_is_manager(transcript_path)

    # Ensures no agent modifies intent.yaml unauthorized.
    if tool_name in ["replace_file_content", "write_to_file", "multi_replace_file_content"]:
        target_path = tool_args.get("TargetFile", "") or tool_args.get("AbsolutePath", "")
        if "intent.yaml" in target_path:
            if not is_manager:
                log_to_blackboard("Enforcement: Blocked unauthorized modification of intent.yaml by non-manager")
                print(json.dumps({
                    "decision": "deny",
                    "reason": "STRICT ENFORCEMENT: Only the Scrum Master can modify intent.yaml."
                }))
                return

    # Only blindfold specific read tools
    if tool_name not in ["view_file", "grep_search", "list_dir", "find_by_name"]:
        print(json.dumps({"decision": "allow"}))
        return

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
