#!/usr/bin/env python3
"""
Neurosymbolic Validation Engine for Hermes SCL (Structured Cognitive Loop).
Validates agent handoff JSON payloads strictly using Pydantic.
"""
import sys
import json
from pathlib import Path
from typing import List, Optional

try:
    from pydantic import BaseModel, Field, ValidationError
except ImportError:
    print("FATAL: pydantic is not installed. Run 'pip install pydantic' first.")
    sys.exit(1)

class CodeModification(BaseModel):
    filepath: str = Field(..., description="Absolute or relative path to the modified file")
    change_type: str = Field(..., description="Type of change: CREATE, UPDATE, DELETE")
    description: str = Field(..., description="Short explanation of what was changed")

class TestResult(BaseModel):
    test_command: str = Field(..., description="The command used to test the changes")
    status: str = Field(..., description="Status of the test: PASSED, FAILED")
    output_snippet: str = Field(..., description="Short snippet of the test output proving it passed/failed")

class HandoffPayload(BaseModel):
    task_id: str = Field(..., description="The ID or name of the task completed")
    worker_role: str = Field(..., description="The role of the subagent (e.g. implementer, reviewer)")
    summary: str = Field(..., description="Detailed summary of the work done and decisions made")
    modifications: List[CodeModification] = Field(default_factory=list, description="List of all files changed")
    tests: List[TestResult] = Field(default_factory=list, description="List of tests executed to verify the code")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Worker's confidence score between 0.0 and 1.0")
    requires_human: bool = Field(default=False, description="True if the agent is stuck and requires human lateral thinking")

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

    try:
        # Validate against the Pydantic schema
        payload = HandoffPayload(**data)
        print("✅ SUCCESS: Neurosymbolic Validation Passed.")
        print(f"Task: {payload.task_id} | Role: {payload.worker_role} | Confidence: {payload.confidence_score}")
        print(f"Modifications: {len(payload.modifications)} files | Tests: {len(payload.tests)} run")
        
        # Enforce business logic on top of syntax
        if not payload.requires_human and len(payload.modifications) > 0 and len(payload.tests) == 0:
            print("=> FATAL LOGIC ERROR: Modifications were made but NO tests were run! [MANDATORY_TDD Rule Violated]")
            return False

        if payload.confidence_score < 0.7 and not payload.requires_human:
            print("=> WARNING: Confidence is too low (<0.7) but human intervention wasn't requested. Reviewer must scrutinize.")

        return True

    except ValidationError as e:
        print("=> ERROR: Neurosymbolic Schema Validation Failed.")
        print(e.json())
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_handoff.json>")
        sys.exit(1)
    
    target = Path(sys.argv[1]).resolve()
    success = validate_handoff(target)
    sys.exit(0 if success else 1)
