---
id: issue-049
title: "Fix changelog version bump calculation and branch-based issue injection"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3, CLI Commands
- **Architecture**: Refactor `changelog.py` to get current branch and automatically inject branch closed issues when there are no new commits on the branch, ensuring version bumps and detailed changelog entries work correctly.
- **Key Modules**:
  - [.agents/scripts/cli/commands/changelog.py](file://./.agents/scripts/cli/commands/changelog.py)
  - [CHANGELOG.md](file://./CHANGELOG.md)
  - [AGENTS.md](file://./AGENTS.md)
  - [bootstrap.sh](file://./bootstrap.sh)
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)

## 2. Implementation Subtasks
- [x] Acquire module locks for `changelog` <!-- id: subtask-locks -->
- [x] Define branch-based conventional commit injection in `changelog.py` to prevent `No notable changes` and missing version bumps <!-- id: subtask-changelog-bump-fix -->
- [x] Clean up and align past versions in `CHANGELOG.md`, `AGENTS.md`, `bootstrap.sh`, and `bootstrap.py` <!-- id: subtask-changelog-cleanup -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] Running the changelog generator on an issue branch correctly bumps version and adds the issue title even if no commits are present.
