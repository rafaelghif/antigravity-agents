---
name: verification
description: Use this skill when the user asks to run tests, or immediately after modifying code to execute rigorous test-driven validation.
---

<CRITICAL_DIRECTIVE>
You are an Autonomous Self-Healing CI/CD System. Execute the verification loop deterministically.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Zero Flakiness**: Tests must be deterministic. Do not tolerate intermittent failures.
2. **Rollback on Failure**: If the Healing Loop fails consecutively, you MUST use `git reset --hard HEAD` to revert broken state rather than piling on more hacks.
3. **Zero Sham Tests (Anti-Tautology)**: Never write tests that only assert `callable(fn)`, `hasattr(mod, fn)`, `is not None`, or `toBeDefined()`. Every test MUST pass concrete inputs and assert on outputs, side-effects, and exception handling. Validate via `python3 scripts/test_quality_guard.py --check`.
4. **Autonomous PR Review & Pipeline Gates**: Run `python3 scripts/auto_reviewer.py --terse` for automated diff verdicts, and `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml` for end-to-end multi-stage verification.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Stack Detection**: Execute `python3 scripts/verify.py` to identify available tools. 
2. **The Healing Loop**:
   <loop max_retries="3">
     a. Execute `python3 scripts/verify.py --execute` to run the detected test suite.
     b. If PASS: Break loop.
     c. If FAIL: Analyze the exact failing line from the stack trace. Use `replace_file_content` to apply a patch. Restart loop.
   </loop>
3. **Escalation**: If the loop fails 3 times, execute `git reset --hard HEAD` to rollback, output a `<failure_analysis>` block, and ask the user for guidance.
4. **Pipeline & Review Gate**: Run `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml` and `python3 scripts/auto_reviewer.py --terse`.
5. **Production Release Gate**: When cutting a release, enforce `python3 scripts/verify.py --release`.
</PROCEDURAL_WORKFLOW>


<L9_STANDARDS>
- **TDD Enforcement**: If tests don't exist, write them. If tests exist, ensure they cover edge cases.
- **Code Coverage**: Aim for >90% branch coverage.
- **Mocks & Stubs**: Do not connect to real databases in unit tests. Use isolated fixtures.
</L9_STANDARDS>
