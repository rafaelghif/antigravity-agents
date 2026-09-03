#!/usr/bin/env python3
import sys
try:
    from scripts.yaml_loader import load_yaml
except ImportError:
    from yaml_loader import load_yaml
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def compile_intent(file_path):
    print(f"[INTENT COMPILER] Validating strict intent specification from {file_path}...")
    if not os.path.exists(file_path):
        print(f"ERROR: Intent Validation Failed. File '{file_path}' does not exist. Vibe coding blocked.")
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            intent = load_yaml(f.read())
            
        if not isinstance(intent, dict):
            raise ValueError("Intent must be a YAML dictionary mapping.")
            
        required_fields = ["name", "status"]
        for field in required_fields:
            if field not in intent:
                raise ValueError(f"Missing required strict field: '{field}'")
                
        status = str(intent.get("status", "")).upper()
        if status not in ("IN_PROGRESS", "DONE"):
            raise ValueError(f"Status must be 'IN_PROGRESS' or 'DONE', got '{status}'")

        # Validate list structures if present
        for list_key in ("objectives", "constraints", "core_philosophy"):
            items = intent.get(list_key)
            if items is not None and not isinstance(items, list):
                raise ValueError(f"Field '{list_key}' must be a list if defined.")

        print(f"[INTENT COMPILER] Validation passed. Intent '{intent['name']}' (status: {status}) conforms to AAC standards.")
        
        out_dir = ROOT / ".agents" / "harness"
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "compiled_intent.json", "w", encoding="utf-8") as out:
            json.dump(intent, out, indent=2)
            
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax. Vibe coding blocked.\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Intent Validation Failed. Vibe coding blocked.\n{e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: intent_compiler.py <intent.yaml>")
        sys.exit(1)
    compile_intent(sys.argv[1])
