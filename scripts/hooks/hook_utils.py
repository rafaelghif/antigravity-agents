import sys
import json

def read_hook_payload() -> dict:
    raw_input = sys.stdin.buffer.read().decode('utf-8', errors='replace').strip()
    if not raw_input:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
    try:
        return json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"[hook] Error parsing stdin: {e}\n")
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
