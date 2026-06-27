---
id: issue-060
title: "Improve CLI helper UI, add help commands, and projects.json sample"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Basic text help printing.
  - *Trade-offs*: Poor visual aesthetics, lacks rich guidance for subcommand parameters.
- **Option B (Recommended)**: Add interactive terminal colors, support `--help`, `-h`, `help` and subcommand-specific usages. Write `.agents/projects.example` sample with explicit optional/required keys.
  - *Trade-offs*: Clean, highly professional, improves overall UX of the framework.

## 2. Technical Decisions
- **Stack**: Python 3, JSON.
- **Key Modules**:
  - [.agents/scripts/cli/helper.py](file://./.agents/scripts/cli/helper.py)
  - [.agents/projects.example](file://./.agents/projects.example)
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [install.sh](file://./install.sh)

## 3. Implementation Subtasks
- [x] Create `.agents/projects.example` with detailed required/optional parameter documentation <!-- id: subtask-create-projects-example -->
- [x] Update `install.sh` and `bootstrap.py` to copy `.agents/projects.example` to target project directories <!-- id: subtask-copy-projects-example -->
- [x] Refactor `helper.py` to support `--help`, `-h`, `help`, and command-specific help with modern colored interactive UI <!-- id: subtask-improve-cli-ui -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Running `./helper.sh help` or `./helper.sh --help` prints the beautifully formatted command list
- [x] Running `./helper.sh help bootstrap` or `./helper.sh bootstrap --help` prints bootstrap-specific parameters
- [x] `.agents/projects.example` is created and correctly copied during installation and bootstrapping
- [x] `./helper.sh validate` passes successfully without errors
