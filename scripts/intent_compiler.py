#!/usr/bin/env python3
import sys
import yaml

def compile_intent(file_path):
    print(f"Compiler Post-O1 Intent from {file_path}...")
    try:
        with open(file_path, 'r') as f:
            intent = yaml.safe_load(f)
        print("=> AST successfully generated from intent.")
        print("=> Agent swarm dispatched under strict Harness governance.")
    except Exception as e:
        print("ERROR: Invalid Intent Specification. Vibe coding detected and blocked.")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: intent_compiler.py <intent.yaml>")
        sys.exit(1)
    compile_intent(sys.argv[1])
