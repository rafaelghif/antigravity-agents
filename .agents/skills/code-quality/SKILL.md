---
name: code-quality
description: Use this skill when the user asks to write, refactor, or review application code to ensure enterprise-grade maintainability.
---

<CRITICAL_DIRECTIVE>
Enforce Staff-level procedural rigor and Enterprise-Grade software architecture during implementation.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **SOLID Principles**: Enforce Single Responsibility (SRP) and Dependency Inversion (DIP). Classes and functions must have precisely one reason to change.
2. **Cyclomatic Complexity**: Functions must be atomic and strictly limited in indentation depth. Refactor deeply nested loops or conditionals into explicit private helper methods.
3. **Self-Documenting Code**: Mandate descriptive, domain-driven variable and function names. Restrict comments exclusively to explaining "Why" the business logic exists.
4. **Resilient Error Handling**: Enforce strict error boundaries. Catch specific exceptions, attach diagnostic context, and ensure graceful degradation.
5. **Feature Completeness (Anti-Dummy)**: No "half-assed" implementations. You MUST write end-to-end functionality including database persistence, error routing, and type-safe contracts. NEVER leave placeholders, mock arrays, or hardcoded stubs.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Context Acquisition**: You must fully read and understand a file's content and imports prior to executing any modifications.
2. **Minimal Delta Enforcement**: Only apply the exact changes requested. Strip out speculative or unrelated refactorings from your plan.
3. **Test Gap Analysis**: Check the adjacent test file. If the modified behavior is uncovered, you MUST write the corresponding test case.
4. **Local Verification**: Run the stack's linter and test runner (via `python3 scripts/verify.py --execute` or native commands).
5. **Diff Review**: Inspect your own diff. Ensure no debugging statements or residual dead code remains.
</PROCEDURAL_WORKFLOW>
