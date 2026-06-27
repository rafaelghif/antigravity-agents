---
id: issue-011
title: "Set up automated compliance validation suite"
status: open
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification: V2 Compliance Validation Suite

This issue outlines the integration of new compliance checks into `.agents/scripts/validate.py`.

## 1. Technical Decisions

### New Validation Checks
1. **Task Board Format Check**: Verifies that `.agents/tasks/board.md` has the headers `## Todo`, `## Doing`, and `## Done`, and that task IDs follow correct format.
2. **Static Code Linting Check**: Runs `flake8` syntax validation on all changed Python files. If `flake8` is not installed, it falls back to Python's built-in `py_compile` module to verify syntax.
3. **Automated Test Run**: Executes the project's test suite (via the command detected by `recon.py`, e.g., `pytest`) before a commit is allowed.
   - **Bypass Rule**: Allow bypassing test execution if environment variable `BYPASS_TESTS=true` is set.

## 2. Implementation Subtasks
- [ ] Add `board.md` format verification logic in `validate.py`.
- [ ] Add static syntax compiling / linter check logic in `validate.py`.
- [ ] Add test suite execution logic in `validate.py` (reads test command from `.agents/rules.md` or `recon.py`).
- [ ] Implement support for `BYPASS_TESTS` environment variable to skip test execution.

## 3. Acceptance Criteria
- [ ] Running `./helper.sh validate` successfully checks `board.md` syntax.
- [ ] Adding invalid Python syntax causes the validation suite to fail.
- [ ] Commits are blocked if unit tests fail, unless `BYPASS_TESTS=true` is set.
