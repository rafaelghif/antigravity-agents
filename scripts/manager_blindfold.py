import sys
import json
import os
import subprocess
import glob
import time
import re

def log_to_blackboard(msg):
    try:
        subprocess.run(["python3", "scripts/inbox_manager.py", "send", "manager_blindfold", "all", msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
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

def get_agent_role(transcript_path: str) -> str:
    if not transcript_path or not os.path.exists(transcript_path):
        return "primary"
    try:
        with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("type") == "USER_INPUT":
                    content = entry.get("content", "")
                    if "Principal Agile Orchestrator" in content or "scrum-master" in content or "Scrum Master" in content:
                        return "scrum-master"
                    if "Principal Product Manager" in content or "product-manager" in content:
                        return "product-manager"
                    if any(worker in content for worker in ["staff-backend", "frontend-architect", "database-sre", "devsecops-principal", "qa-automation-lead"]):
                        return "worker"
                break
    except Exception as e:
        sys.stderr.write(f"Transcript read notice: {e}\n")
    return "primary"

def main():
    payload = sys.stdin.read()
    if not payload:
        print(json.dumps({"decision": "allow"}))
        return
        
    try:
        data = json.loads(payload)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})
    transcript_path = data.get("transcriptPath", "")

    enforce_timeouts()
    role = get_agent_role(transcript_path)

    # Ensures worker agents do not modify intent.yaml directly
    if tool_name in ["replace_file_content", "write_to_file", "multi_replace_file_content"]:
        target_path = tool_args.get("TargetFile", "") or tool_args.get("AbsolutePath", "")
        if "intent.yaml" in target_path:
            if role == "worker":
                log_to_blackboard("Enforcement: Blocked unauthorized modification of intent.yaml by worker agent")
                print(json.dumps({
                    "decision": "deny",
                    "reason": "STRICT ENFORCEMENT: Workers cannot modify intent.yaml. Only the Product Manager or Scrum Master can modify intent."
                }))
                return

    # Only blindfold specific read tools for Scrum Master
    if tool_name not in ["view_file", "grep_search", "list_dir", "find_by_name"]:
        print(json.dumps({"decision": "allow"}))
        return

    if role == "scrum-master":
        target_path = ""
        if tool_name == "view_file":
            target_path = tool_args.get("AbsolutePath", "")
        elif tool_name == "grep_search":
            target_path = tool_args.get("SearchPath", "")
            
        # The Scrum Master is allowed to inspect orchestration, blackboard, intent, tasks, and memory
        allowed_paths = ["state.json", "inbox", "tasks", "intent.yaml", "handoff", ".agents/brain", ".agents/plans", "audit.log"]
        if not any(ap in target_path for ap in allowed_paths):
            print(json.dumps({
                "decision": "deny",
                "reason": "RBAC BLINDFOLD: As the Scrum Master, you are strictly forbidden from reading source code directly. You MUST spawn a sub-agent (e.g. staff-backend or devsecops-principal) to read and analyze these files for you, and coordinate with them via the Blackboard."
            }))
            return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
