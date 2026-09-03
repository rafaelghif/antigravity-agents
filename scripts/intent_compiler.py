#!/usr/bin/env python3
import sys
try:
    import yaml
except ImportError:
    print("Error: 'yaml' module not found. Please install it using: pip install pyyaml", file=sys.stderr)
    sys.exit(1)
import json
import os

def compile_intent(file_path):
    print(f"[INTENT COMPILER] Validating strict intent specification from {file_path}...")
    if not os.path.exists(file_path):
        print(f"ERROR: Intent Validation Failed. File '{file_path}' does not exist. Vibe coding blocked.")
        sys.exit(1)
        
    try:
        with open(file_path, 'r') as f:
            intent = yaml.safe_load(f)
            
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
        
        os.makedirs(".agents/harness", exist_ok=True)
        with open(".agents/harness/compiled_intent.json", "w") as out:
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
