---
name: verification
description: Use this skill when executing tests, validating code changes, diagnosing test failures with the autonomous healing loop, or enforcing anti-sham testing standards.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.46.0"
  category: quality-assurance
  tags: [testing, anti-sham, verification, tdd, healing-loop]
---

# Verification, Anti-Sham Testing & Autonomous Healing Protocol

**Role**: Principal QA Automation Architect & LLM Reliability Lead.

## Overview & Trigger Conditions
Activate this skill whenever validating code modifications, running test suites, diagnosing test failures, implementing automated test suites, or checking release readiness.

**Trigger Scenarios & Keywords**:
- Running tests, writing unit/integration tests, test-driven development (TDD), fixing broken tests.
- Keywords: `test`, `tests`, `testing`, `pytest`, `jest`, `unit`, `e2e`, `assert`, `coverage`, `spec`, `mock`, `integration`, `verify`.

## Core Standards & Invariants

1. **Zero Sham Tests (Anti-Tautology)**:
   - **Banned Test Anti-Patterns**: Never write tests that only assert `callable(fn)`, `hasattr(mod, fn)`, `is not None`, `toBeDefined()`, or `assertTrue(True)`.
   - Every test MUST exercise concrete execution logic: pass varied inputs, trigger mutations, and assert on return values, state changes, and specific exception types.
   - Enforce continuously via: `python3 scripts/test_quality_guard.py --check`.

2. **Never Weaken Existing Tests**:
   - NEVER comment out, remove, or weaken assertions in existing test suites to make CI pass.
   - A failing existing test is empirical proof of a regression; fix the underlying implementation, not the test.

3. **Determinism & Zero Flakiness**:
   - Tests must run deterministically across all environments without race conditions or intermittent failures.
   - Avoid sleeping in tests (`time.sleep()`); await explicit events, promises, or mock external I/O clocks.

4. **Test Pyramid & Mocking Discipline**:
   - Emphasize fast, hermetic unit tests covering edge cases: null/empty inputs, boundary limits, and error paths.
   - **Strict Mock Boundaries**: Mocks are strictly restricted to external I/O boundaries (HTTP requests, message queues, third-party vendor APIs). Never mock internal domain models or business logic.

5. **Multi-Stage Verification Gate**:
   - All code changes must pass all 9 technical gates:
     `python3 scripts/verify.py --execute --terse`
   - Gate failures block merges; zero regressions tolerated.

## Golden Example: Anti-Sham vs Behavioral Invariant Test
```python
# BAD (Sham): Tautological presence check without executing behavior
self.assertTrue(callable(calculate_order_total))
self.assertIsNotNone(order.calculate_tax)

# GOOD (Golden Behavioral Test): Executes real business logic & boundaries
result = calculate_order_total(
    subtotal=100.0,
    discount_pct=0.15,
    tax_rate=0.08
)
self.assertEqual(result.discount_amount, 15.0)
self.assertEqual(result.tax_amount, 6.80)
self.assertEqual(result.final_total, 91.80)
```

## The Autonomous Healing Loop
When encountering test failures, follow this deterministic loop:
1. **Execute**: Run `python3 scripts/verify.py --execute --terse`.
2. **Analyze**: Pinpoint root cause from failure trace and exact line number.
3. **Patch & Retest**: Apply smallest correct fix via `replace_file_content` and re-verify.
4. **Circuit Breaker**: If unresolved after 3 attempts, halt immediately. Do not pile hacks on broken state; run `git reset --hard HEAD` to restore clean baseline.

## Procedural Workflow
1. **Ground Stack**: Run `python3 scripts/verify.py` to identify configured test runners.
2. **Execute Tests**: Run domain unit tests and `python3 scripts/test_quality_guard.py --check`.
3. **Workflow Gate**: Validate `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml`.
4. **Autonomous Review**: Run `python3 scripts/auto_reviewer.py --terse`.
5. **Release Gate**: Prior to shipping a release, run `python3 scripts/verify.py --release`.

## Anti-Patterns & Common Pitfalls
- **Fabricating Test Evidence**: Claiming tests pass without actually executing them in the terminal.
- **Tautological Assertions**: Writing tests that test the test framework rather than system logic (`self.assertEqual(1, 1)`).
- **Over-Mocking**: Mocking internal domain classes so deeply that tests pass even if core logic is completely broken.
