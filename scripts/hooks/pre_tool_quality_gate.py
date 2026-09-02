import sys, json
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from hook_utils import read_hook_payload
import re
from pathlib import Path

def main():
    payload = read_hook_payload()
        
    tool_name = payload.get("toolCall", {}).get("name", "")
    if tool_name not in ["write_to_file", "replace_file_content"]:
        print(json.dumps({"decision": "allow"}))
        return
        
    args = payload.get("toolCall", {}).get("args", {})
    target_file = args.get("TargetFile", "")
    
    if re.search(r"tasks/.*\.yaml$", target_file):
        print(json.dumps({"decision": "allow"}))
        return
        
    if not Path("tasks").is_dir():
        print(json.dumps({
            "decision": "ask",
            "reason": "CRITICAL PROTOCOL VIOLATION: You bypassed the /grill-me phase! You are STRICTLY FORBIDDEN from writing code before gathering requirements. You MUST initiate the /grill-me interactive interview using ask_question to align on requirements. Then, you MUST split the architecture into atomic micro-tasks and save them inside the 'tasks/' directory (e.g., tasks/01_auth.yaml). DO NOT write source code yet."
        }))
        return
        
    if re.search(r"\.(py|ts|js|cs)$", target_file):
        if not re.search(r"test_|spec\.|\.test\.|tests/|scripts/|\.agents/|setup\.py|Test", target_file):
            basename = Path(target_file).name
            name_without_ext = Path(target_file).stem
            ext = Path(target_file).suffix[1:]
            
            test_exists = False
            try:
                for f in Path(".").rglob(f"*{name_without_ext}*"):
                    if "node_modules" in f.parts or ".venv" in f.parts or ".git" in f.parts:
                        continue
                    if re.search(r"test_|spec\.|\.test\.|Test", f.name):
                        test_exists = True
                        break
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")
            
            if not test_exists:
                print(json.dumps({
                    "decision": "ask",
                    "reason": f"TDD VIOLATION: You are attempting to write source code ('{basename}') BEFORE writing its test file! World-class Agentic Standard mandates Test-Driven Development (TDD). You MUST write the test file (e.g., 'test_{basename}' or '{name_without_ext}.test.{ext}') FIRST, before you are allowed to modify the implementation."
                }))
                return
                
    desc = args.get("Description") or args.get("Instruction") or ""
    if not re.search(r"complexity|O\(|index|cache|scaling|N\+1", desc, re.IGNORECASE):
        print(json.dumps({
            "decision": "ask",
            "reason": "CRITICAL ENTERPRISE REJECTION: You are bypassing L9 scaling standards! Your tool Description/Instruction MUST explicitly state the Time/Space Complexity (e.g., O(1), O(log N)) AND Database Scaling strategy (e.g., prevents N+1, uses Indexes, Caching). Re-evaluate your code, ensure it is horizontally scalable, and call the tool again with a proper engineering justification."
        }))
        return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
