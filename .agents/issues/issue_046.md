---
id: issue-046
title: "Fix changelog boundary commit resolution and clean up duplicated changelog entries"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3, Git CLI
- **Architecture**: Fix `get_boundary_commit` in `changelog.py` to correctly resolve the previous version release commit using the `chore(release):` keyword. Clean up the polluted `CHANGELOG.md` file.
- **Key Modules**:
  - [.agents/scripts/cli/commands/changelog.py](file://./.agents/scripts/cli/commands/changelog.py)
  - [CHANGELOG.md](file://./CHANGELOG.md)

## 2. Implementation Subtasks
- [x] Acquire module locks for `changelog` <!-- id: subtask-locks -->
- [x] Refactor `get_boundary_commit` in `changelog.py` to identify the boundary release commit using standard release message queries <!-- id: subtask-changelog-fix -->
- [x] Clean up the duplicate historical entries from `CHANGELOG.md` and keep only the real changelog entries for each release <!-- id: subtask-changelog-cleanup -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] Running the changelog generator only extracts commits on the current branch since the last release commit
- [x] The `CHANGELOG.md` is clean, readable, and does not contain duplicated historical commits across versions
