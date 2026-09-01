import sys
import json
import os
import re
from pathlib import Path

SUBAGENT_SIGNATURES = re.compile(r"staff-backend|frontend-architect|database-sre|devsecops-principal|qa-automation-lead|product-manager|scrum-master|L9 Staff|L9 Principal|L9 Expert|Execute task|subagent:\s*true", re.I)

def is_authorized_subagent(transcript_path: str) -> bool:
    if not transcript_path or not os.path.exists(transcript_path):
        return False
    try:
        head_text = "".join(Path(transcript_path).read_text(encoding="utf-8", errors="ignore").splitlines()[:5])
        return bool(SUBAGENT_SIGNATURES.search(head_text))
    except Exception as e:
        sys.stderr.write(f"Delegation guard notice: {e}\n")
        return False

def main():
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        print(json.dumps({"decision": "allow"}))
        return

    try:
        hook_payload = json.loads(raw_input)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    if is_authorized_subagent(hook_payload.get("transcriptPath", "")):
        print(json.dumps({"decision": "allow"}))
        return

    tool_args = hook_payload.get("toolCall", {}).get("args", {})
    target_file = tool_args.get("TargetFile", "") or tool_args.get("AbsolutePath", "")
    
    # We allow the Primary Agent to modify framework files (.md docs, config, scripts)
    # But we FORBID it from touching application code (e.g., src/, app/, lib/)
    path_parts = [p.lower() for p in Path(target_file).parts]
    is_forbidden = any(fd in path_parts for fd in ["src", "app", "lib"])
    
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
