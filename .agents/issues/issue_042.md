---
id: issue-042
title: "Exclude memory, tasks, issues, plans, and tests during installation to guarantee a fresh workspace"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Bash Shell, Python 3
- **Architecture**: Enforce absolute isolation of active core agent history, memory registers, task boards, and test scripts when copying/installing the core agent system to target directories.
- **Key Modules**:
  - [install.sh](file://./install.sh)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Refactor `install.sh` to explicitly exclude `memory/`, `tasks/`, `issues/`, `plans/`, and `tests/` directories during copy operations <!-- id: subtask-installer-exclude -->
- [x] Add unit test assertions to verify that active metadata folders are never copied during bootstrapping <!-- id: subtask-tests -->
- [x] Release locks, run validation, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] Installing the agent to a target project directory via `install.sh` results in a fresh workspace containing no pre-existing issues, task board tasks, developer plan files, or test scripts from the core repository.
