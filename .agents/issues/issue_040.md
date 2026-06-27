---
id: issue-040
title: "Remediate technical debt in issue CLI, validation guard, and bootstrap scripts"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3, Bash Shell
- **Architecture**: Refactoring existing CLI command dispatchers, validation audits, and bootstrapping/installer procedures.
- **Key Modules**:
  - [.agents/scripts/cli/commands/issue.py](file://./.agents/scripts/cli/commands/issue.py)
  - [.agents/scripts/validate.py](file://./.agents/scripts/validate.py)
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [install.sh](file://./install.sh)
  - [bootstrap.sh](file://./bootstrap.sh)

## 2. Implementation Subtasks
- [x] Acquire module locks for `issue`, `validate`, and `bootstrap` <!-- id: subtask-locks -->
- [x] Refactor `issue.py` to use robust parsing, checklist counting under `## Tasks`, and graceful checkouts <!-- id: subtask-issue-cli -->
- [x] Add `--skip-subtasks` / `SKIP_SUBTASK_AUDIT` to `validate.py` and clean up inline imports <!-- id: subtask-validate -->
- [x] Refactor `bootstrap.py` and `bootstrap.sh` to read `AGENTS.md` and rules from source files without duplication <!-- id: subtask-bootstrap -->
- [x] Add unit test coverage for the `--skip-subtasks` validation behavior and new bootstrap behaviors <!-- id: subtask-tests -->
- [x] Release locks, run validation, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] The `bootstrap.py` script no longer contains a hardcoded inline copy of the `AGENTS.md` template
- [x] The `--skip-subtasks` flag successfully bypasses unfinished tasks check during active development
