---
id: issue-106
title: "Implement Automatic Non-Interactive Mode Detection and Commit Message Validation"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3
- **Architecture**: Automated execution safety
- **Key Modules**:
  - [interactive.py](file://./.agents/scripts/cli/interactive.py)
  - [learn.py](file://./.agents/scripts/cli/commands/learn.py)
  - [bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [validate.py](file://./.agents/scripts/validate.py)

## 2. Implementation Subtasks
- [x] Add `ANTIGRAVITY_AGENT` environment variable checks to disable interactive menus in `interactive.py`, `learn.py`, and `bootstrap.py`
- [x] Add a `Commit Message Format Audit` (Audit 10) in `validate.py` to programmatically verify that commits on the current branch follow Conventional Commits and reference the issue ID
- [x] Lock `validate` and `bootstrap` modules
- [x] Verify validation and unit tests pass successfully

## 3. Acceptance Criteria
- [x] Running scripts with `ANTIGRAVITY_AGENT=1` automatically skips prompts and resolves defaults
- [x] Validation fails if any commit message on the current branch has invalid conventional commit prefix or lacks issue ID
- [x] Validation succeeds on clean compliance
