import sys, json, re
from pathlib import Path

def main():
    try:
        payload = json.loads(sys.stdin.read().strip())
    except:
        print(json.dumps({"decision": "allow"}))
        return
        
    subagents = payload.get("toolCall", {}).get("args", {}).get("Subagents", [])
    if not subagents:
        print(json.dumps({"decision": "allow"}))
        return
        
    for sa in subagents:
        prompt = sa.get("Prompt", "")
        if not re.search(r"tasks/[0-9a-zA-Z_]+\.yaml", prompt):
            print(json.dumps({
                "decision": "ask",
                "reason": "CRITICAL CONTEXT BLOAT PREVENTED: You must not bundle instructions. Split the task into small, isolated files inside a 'tasks/' directory (e.g., 'tasks/01_auth.yaml'). Your delegation prompt MUST explicitly reference the specific 'tasks/*.yaml' file the subagent should execute."
            }))
            return
            
        m = re.search(r"(tasks/[0-9a-zA-Z_]+\.yaml)", prompt)
        if m:
            task_file = m.group(1)
            if not Path("tasks").is_dir() or not Path(task_file).is_file():
                print(json.dumps({
                    "decision": "ask",
                    "reason": f"PHYSICAL VERIFICATION FAILED: You referenced '{task_file}', but it does not exist on disk! You MUST use write_to_file to physically create the 'tasks/' directory and generate the atomic micro-task YAML files before delegating."
                }))
                return
                
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
