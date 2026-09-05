---
name: verification-gates
description: Strict test-driven verification, anti-sham testing, and mandatory evidence validation.
trigger: always_on
---

# Verification-First Execution & Anti-Sham Testing

- **Verify With Evidence**: Every change must be verified with actual test execution (`python3 scripts/verify.py --execute --terse` and domain test suites). Never claim a task is "working" or "fixed" without executable test output evidence.
- **Zero Sham Tests**: Tests must assert non-trivial behavior, return values, state mutations, and exception paths. Tests that merely assert `callable()`, `hasattr()`, or `is not None` without executing logic are strictly banned.
- **Never Weaken Tests**: Never modify, comment out, or delete an existing test to make a suite pass. Existing test failures are signals of unintended regressions.
- **Boundary & Error Probing**: Test null/empty inputs, boundary conditions, and error paths explicitly.
