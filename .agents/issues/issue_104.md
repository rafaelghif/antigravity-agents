---
id: issue-104
title: "Align release version history, resolve double-bumping bug, and format CHANGELOG.md"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: System configurations
- **Architecture**: Version control and changelog consistency
- **Key Modules**:
  - [CHANGELOG.md](file://./CHANGELOG.md)
  - [AGENTS.md](file://./AGENTS.md)
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [bootstrap.sh](file://./bootstrap.sh)
  - [bootstrap.ps1](file://./bootstrap.ps1)

## 2. Implementation Subtasks
- [x] Align the version to `2.83.0` across all files to resolve the double-bumping release duplicates
- [x] Format `CHANGELOG.md` to show a clean, clean progression from `2.80.0` to `2.83.0` without duplicate version entries
- [x] Lock `bootstrap` and update task board

## 3. Acceptance Criteria
- [x] `CHANGELOG.md` matches the clean SemVer timeline
- [x] Version is `2.83.0` in all version-controlled files
- [x] Validation and tests pass successfully
