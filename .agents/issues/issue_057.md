---
id: issue-057
title: "Fix install.sh piping compatibility for unbound BASH_SOURCE variable"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Remove curl piping support and require manual cloning.
  - *Trade-offs*: Degrades UX, breaks standard quick-install procedures.
- **Option B (Recommended)**: Use standard bash empty fallback variables (`${BASH_SOURCE[0]:-}`) to prevent unbound variable crashes, and only use local source if `SRC_DIR` is determined successfully.
  - *Trade-offs*: Extremely robust, fully supports curl piped installation, zero side-effects.

## 2. Technical Decisions
- **Stack**: Bash scripting.
- **Key Modules**:
  - [install.sh](file://./install.sh)

## 3. Implementation Subtasks
- [x] Guard `BASH_SOURCE` lookup using `${BASH_SOURCE[0]:-}` and ensure `SRC_DIR` is only set if BASH_SOURCE is non-empty <!-- id: subtask-guard-bash-source -->
- [x] Update local directory scan in `install.sh` to require a non-empty `SRC_DIR` <!-- id: subtask-src-dir-check -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Executing `install.sh` via piped stdin (curl | bash) does not fail with unbound variable errors
- [x] `./helper.sh validate` passes successfully without errors
