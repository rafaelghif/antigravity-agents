---
id: issue-058
title: "Synchronize bootstrap.ps1 versions and verify local file installer options"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Manual version bumps in Windows bootstrap script.
  - *Trade-offs*: Error prone, versions will drift between systems.
- **Option B (Recommended)**: Integrate `bootstrap.ps1` version updating in `changelog.py` so both shell and PowerShell bootstrappers are in sync.
  - *Trade-offs*: Maintains release consistency across platforms, fully automated.

## 2. Technical Decisions
- **Stack**: Python 3, PowerShell.
- **Key Modules**:
  - [bootstrap.ps1](file://./bootstrap.ps1)
  - [.agents/scripts/cli/commands/changelog.py](file://./.agents/scripts/cli/commands/changelog.py)

## 3. Implementation Subtasks
- [x] Synchronize current hardcoded versions in `bootstrap.ps1` to `2.30.3` <!-- id: subtask-ps1-version-sync -->
- [x] Implement `bootstrap.ps1` version auto-updater in `changelog.py` <!-- id: subtask-changelog-ps1-updater -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Version strings match `2.30.3` in `bootstrap.ps1`
- [x] `./helper.sh validate` passes successfully without errors
