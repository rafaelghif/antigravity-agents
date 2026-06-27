---
id: issue-061
title: "Enforce remote Git source download by default during installation"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Remove local copy logic completely from installer.
  - *Trade-offs*: Developer cannot run local integration tests before pushing, slowing down debugging loop.
- **Option B (Recommended)**: Require `ANTIGRAVITY_LOCAL_DEV=1` environment variable for local source copying, forcing standard users to pull latest from remote GitHub Git repository.
  - *Trade-offs*: Extremely robust, user-proof, guarantees up-to-date code.

## 2. Technical Decisions
- **Stack**: Bash scripting.
- **Key Modules**:
  - [install.sh](file://./install.sh)

## 3. Implementation Subtasks
- [x] Refactor `install.sh` local source condition to check for `ANTIGRAVITY_LOCAL_DEV` variable <!-- id: subtask-check-local-dev-env -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Executing `install.sh` without `ANTIGRAVITY_LOCAL_DEV` set defaults to remote Git GitHub zip download
- [x] Executing `install.sh` with `ANTIGRAVITY_LOCAL_DEV=1` successfully performs local copy install
- [x] `./helper.sh validate` passes successfully without errors
