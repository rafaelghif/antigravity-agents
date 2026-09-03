#!/usr/bin/env python3
"""
Pre-Tool DevSecOps Guard: Protects workspace integrity and prevents secret leakage.
Allows unrestricted coding while blocking raw private keys and .git corruption.
"""
import sys
import json
import re
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from hook_utils import read_hook_payload

SECRET_PATTERNS = [
    r'-----BEGIN\s+(?:RSA|OPENSSH|EC|DSA)\s+PRIVATE\s+KEY-----',
    r'ghp_[a-zA-Z0-9]{36}',
    r'AKIA[0-9A-Z]{16}',
]

def main() -> None:
    payload = read_hook_payload()
    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    
    if tool_name not in ("write_to_file", "replace_file_content"):
        print(json.dumps({"decision": "allow"}))
        return
        
    args = tool_call.get("args", {})
    target_file = str(args.get("TargetFile", ""))
    
    # 1. Protect Git repository internals from accidental corruption
    if "/.git/" in target_file or target_file.startswith(".git/"):
        print(json.dumps({
            "decision": "ask",
            "reason": "SECURITY GUARD: Modifying .git internal repository files directly is forbidden."
        }))
        return

    # 2. Prevent accidental hardcoded private keys / tokens
    content = str(args.get("CodeContent", "")) + " " + str(args.get("ReplacementContent", ""))
    for pat in SECRET_PATTERNS:
        if re.search(pat, content):
            print(json.dumps({
                "decision": "ask",
                "reason": "SECURITY WARNING: Hardcoded private key or API token detected in code payload. Use environment variables or .env instead."
            }))
            return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
