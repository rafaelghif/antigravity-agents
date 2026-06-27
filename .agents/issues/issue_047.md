---
id: issue-047
title: "Implement installer prerequisite audits for Git, Python 3, and network connectivity"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Bash scripting (`install.sh`), PowerShell (`bootstrap.ps1`/`helper.ps1` if relevant)
- **Architecture**: Enforce checks at the beginning of `install.sh` to verify Git, Python 3, and network connectivity (for remote download branch) are present before proceeding with installation, showing clear recommendations and halting if missing.
- **Key Modules**:
  - [install.sh](file://./install.sh)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Implement Git and Python 3 presence checks at the start of `install.sh` <!-- id: subtask-prereq-checks -->
- [x] Implement network connectivity check in `install.sh` when downloading remote sources from GitHub <!-- id: subtask-network-check -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] `install.sh` successfully aborts with descriptive recommendations if Git or Python 3 is missing, or if network connectivity is down in download mode.
