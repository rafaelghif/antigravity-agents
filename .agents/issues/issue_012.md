---
id: issue-012
title: "Add CLI unit testing suite"
status: open
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification: V2 CLI Testing Suite

This issue covers implementing unit tests for our V2 CLI command modules under `.agents/tests/`.

## 1. Technical Decisions

### Testing Layout
- **Test files folder**: `.agents/tests/`
- **Modules to test**:
  - `test_lock.py`: Tests lock acquisition, release, and conflicts.
  - `test_issue.py`: Tests issue create, close, and list logic.
  - `test_commit.py`: Tests email/name profile switching.

### Testing Strategy
- Mock-based isolation using `unittest.mock` to ensure offline execution under 50ms per test.

## 2. Implementation Subtasks
- [ ] Create `.agents/tests/` folder and `__init__.py`.
- [ ] Implement `.agents/tests/test_lock.py` using mock filesystem.
- [ ] Implement `.agents/tests/test_issue.py` using mock files.
- [ ] Implement `.agents/tests/test_commit.py` with mock git shell calls.
- [ ] Update `validate.py` test suite runner to execute tests from `.agents/tests/`.

## 3. Acceptance Criteria
- [ ] Running `./helper.sh validate` successfully discovers and runs the unit tests.
- [ ] All unit tests pass cleanly with zero failures.
