---
id: issue-059
title: "Copy blueprints directory during install and bootstrap"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Exclude blueprints folder from the installer/bootstrapper copy tree.
  - *Trade-offs*: Developers lack references to architectures inside the target directory.
- **Option B (Recommended)**: Explicitly copy `.agents/memory/blueprints/` directory during installation and bootstrap routines.
  - *Trade-offs*: Provides clean documentation out-of-the-box, slight increase in template files.

## 2. Technical Decisions
- **Stack**: Bash scripting, Python 3.
- **Key Modules**:
  - [install.sh](file://./install.sh)
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)

## 3. Implementation Subtasks
- [x] Refactor `install.sh` to copy `.agents/memory/blueprints` to the target directory <!-- id: subtask-install-copy-blueprints -->
- [x] Refactor `bootstrap.py` to copy `.agents/memory/blueprints` to the target directory <!-- id: subtask-bootstrap-copy-blueprints -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Piped installation (`install.sh`) successfully copies `blueprints` folder contents
- [x] Bootstrapper (`bootstrap.py`) copies `blueprints` folder contents when copying core files
- [x] `./helper.sh validate` passes successfully without errors
