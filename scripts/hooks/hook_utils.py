import sys
import json
from pathlib import Path

def read_hook_payload():
    raw_input = sys.stdin.buffer.read().decode('utf-8', errors='replace').strip()
    if not raw_input:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
    try:
        return json.loads(raw_input)
    except Exception as e:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
