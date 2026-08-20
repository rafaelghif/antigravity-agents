import pytest
import subprocess
from pathlib import Path

# 2026 Automated AI Eval Pipeline (Model-as-a-Judge Mock)
def test_anti_dummy_compliance():
    # Ensures no test file or implementation file contains mock tokens
    forbidden_tokens = ["// TODO", "mock_", "dummy_", "password123"]
    src_files = list(Path(".agents").rglob("*.md"))
    
    for f in src_files:
        content = f.read_text(errors="ignore").lower()
        for token in forbidden_tokens:
            # We skip SKILL.md itself because it might contain the forbidden words in its rules
            if "skill.md" not in f.name.lower():
                assert token not in content, f"Agent evaluation failed: Found forbidden token '{token}' in {f}"

def test_security_skill_presence():
    # Evaluate that implementer always has security skill
    impl_content = Path(".agents/agents/implementer.md").read_text()
    assert "security" in impl_content, "Implementer is missing mandatory security context."
