import pytest
import subprocess
from pathlib import Path

# 2026 Automated CI Pipeline (Static Security & Quality Eval)
def test_anti_dummy_compliance():
    # Ensures no test file or implementation file contains mock tokens
    forbidden_tokens = ["// TODO", "mock_", "dummy_", "passw" + "ord123"]
    src_files = list(Path(".agents").rglob("*.md"))
    
    for f in src_files:
        if "skill.md" in f.name.lower():
            continue
        content = f.read_text(errors="ignore").lower()
        found = [t for t in forbidden_tokens if t in content]
        assert not found, f"Agent evaluation failed: Found forbidden tokens {found} in {f}"

def test_security_skill_presence():
    # Evaluate that implementer always has security skill
    impl_content = Path(".agents/agents/implementer.md").read_text()
    assert "security" in impl_content, "Implementer is missing mandatory security context."
