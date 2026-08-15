---
name: code-quality
description: Use this skill when the user asks to write, refactor, or review application code to ensure enterprise-grade maintainability.
---

<CRITICAL_DIRECTIVE>
Enforce Staff-level procedural rigor during implementation.
</CRITICAL_DIRECTIVE>

<PROCEDURAL_WORKFLOW>
1. **Context Acquisition**: Never modify a file without first reading its entire content and understanding its imports.
2. **Minimal Delta Enforcement**: Only apply the exact changes requested. Strip out speculative or unrelated refactorings from your plan.
3. **Test Gap Analysis**: Check the adjacent test file. If the modified behavior is uncovered, you MUST write the corresponding test case.
4. **Local Verification**: Run the stack's linter and test runner (via `scripts/verify.py` or native commands).
5. **Diff Review**: Inspect your own diff. Ensure no debugging statements or residual dead code remains.
</PROCEDURAL_WORKFLOW>
