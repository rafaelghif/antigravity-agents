#!/usr/bin/env python3
"""
Neurosymbolic Validation Engine for Hermes SCL (Structured Cognitive Loop).
Validates agent handoff JSON payloads strictly using Python Standard Library.
Dependency-Free for Consumer Projects.
"""
import sys
import json
from pathlib import Path

try:
    from scripts import platform_guard  # noqa: F401
except ImportError:
    import platform_guard  # noqa: F401

def validate_handoff(json_path: Path) -> bool:
    if not json_path.exists():
        print(f"=> ERROR: Handoff file {json_path} does not exist.")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"=> ERROR: Handoff file {json_path} is not valid JSON. {e}")
        return False

    # Standard Library Neurosymbolic Schema Validation
    required_keys = {"task_id": str, "worker_role": str, "summary": str, "modifications": list, "tests": list, "confidence_score": (int, float), "requires_human": bool}
    
    for key, expected_type in required_keys.items():
        if key not in data:
            print(f"=> ERROR: Neurosymbolic Validation Failed. Missing required key: '{key}'")
            return False
        if not isinstance(data[key], expected_type):
            print(f"=> ERROR: Type mismatch for '{key}'. Expected {expected_type}, got {type(data[key])}")
            return False

    # Validate Nested Objects
    for mod in data["modifications"]:
        if not all(k in mod and isinstance(mod[k], str) for k in ("filepath", "change_type", "description")):
            print("=> ERROR: Invalid schema in 'modifications'. Expected filepath, change_type, description (all strings).")
            return False

    for test in data["tests"]:
        if not all(k in test and isinstance(test[k], str) for k in ("test_command", "status", "output_snippet")):
            print("=> ERROR: Invalid schema in 'tests'. Expected test_command, status, output_snippet (all strings).")
            return False

    print("✅ SUCCESS: Neurosymbolic Validation Passed.")
    print(f"Task: {data['task_id']} | Role: {data['worker_role']} | Confidence: {data['confidence_score']}")
    print(f"Modifications: {len(data['modifications'])} files | Tests: {len(data['tests'])} run")
    
    # Enforce Business Logic
    if not (0.0 <= float(data["confidence_score"]) <= 1.0):
        print(f"=> ERROR: Confidence score must be between 0.0 and 1.0, got {data['confidence_score']}")
        return False

    if not data["requires_human"] and len(data["modifications"]) > 0 and len(data["tests"]) == 0:
        print("=> FATAL LOGIC ERROR: Modifications were made but NO tests were run! [MANDATORY_TDD Rule Violated]")
        return False

    if data["confidence_score"] < 0.7 and not data["requires_human"]:
        print("=> WARNING: Confidence is too low (<0.7) but human intervention wasn't requested. Reviewer must scrutinize.")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_handoff.json>")
        sys.exit(1)
    
    target = Path(sys.argv[1]).resolve()
    success = validate_handoff(target)
    sys.exit(0 if success else 1)
