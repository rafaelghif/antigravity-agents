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
    
    norm_target = target_file.replace("\\", "/")
    if "/.git/" in norm_target or norm_target.startswith(".git/"):
        sys.stderr.write("[DEVSECOPS AUDIT] Direct .git modification detected in payload.\n")

    # 2. Prevent accidental hardcoded private keys / tokens
    content = str(args.get("CodeContent", "")) + " " + str(args.get("ReplacementContent", ""))
    for pat in SECRET_PATTERNS:
        if re.search(pat, content):
            sys.stderr.write("[SECURITY AUDIT] Potential credential/token pattern detected in tool payload.\n")

    # 3. Anti-Regression Telemetry: Track overwrites of existing files
    if tool_name == "write_to_file" and args.get("Overwrite") is True:
        target_path = Path(target_file)
        if target_path.is_file() and target_path.stat().st_size > 200:
            new_code = str(args.get("CodeContent", ""))
            try:
                old_code = target_path.read_text(encoding="utf-8", errors="replace")
                if len(new_code.splitlines()) < (len(old_code.splitlines()) * 0.3):
                    sys.stderr.write(f"[INTEGRITY AUDIT] Target '{target_path.name}' overwrite ({len(new_code.splitlines())} lines vs {len(old_code.splitlines())} lines).\n")
            except Exception as exc:
                sys.stderr.write(f"Pre-tool check notice: {exc}\n")

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
