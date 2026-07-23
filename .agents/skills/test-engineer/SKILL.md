---
name: test-engineer
description: Unit, integration, and E2E test generation and execution
instruction: Use when adding new features or fixing bugs to maintain test coverage and ensure reliability.
requires_core: ">=4.0.0"
---
# Test Engineer Skill

## Objective
Ensure code reliability by maintaining or improving test coverage across unit, integration, and E2E boundaries.

## When to Execute
- After implementation is complete, before pushing code or creating a PR.
- When fixing flaky tests.

## Execution Steps
1. **Unit Tests**: Generate tests for all new functions/methods.
2. **Integration Tests**: Write tests for new API endpoints and database operations.
3. **E2E Tests**: Implement tests for critical user journeys.
4. **Coverage**: Store current coverage in `.agents/brain/coverage-baseline.json` at project start. Run test suite and ensure coverage percentage is maintained or improved against the baseline across unit, integration, and E2E tests.
5. **Snapshot Tests**: Update or create snapshot tests for UI components.
6. **Flaky Test Detection**: If tests fail intermittently, retry up to `retries.flaky_tests_max` (see `.agents/config.json`). Document flakes in `.agents/incidents/flaky-tests-<date>.md`.
