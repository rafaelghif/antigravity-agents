---
id: issue-064
title: "Add issue.py to auto-staged files list and commit it"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The changes to `issue.py` made in `issue-063` were not committed to the feature branch because `issue.py` is not present in the `files_to_stage` list in `.agents/scripts/cli/commands/issue.py`'s `close` action. We need to add `.agents/scripts/cli/commands/issue.py` to `files_to_stage` to prevent future regressions when modifying the issue CLI scripts.

## Pre-Implementation Impact Analysis

### Option A: Just commit issue.py manually / via Git
* **Pros**: Simple, minimal code changes.
* **Cons**: Any future changes to the issue management command (`issue.py`) will require manual staging or will be left uncommitted.

### Option B: Add issue.py to files_to_stage in issue.py (Recommended)
```python
files_to_stage = [
    path,
    ".agents/tasks/board.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "bootstrap.sh",
    "bootstrap.ps1",
    ".agents/scripts/cli/commands/bootstrap.py",
    "README.md",
    ".agents/scripts/cli/commands/issue.py"
]
```
* **Pros**: Automatically tracks and stages changes to the issue command itself on closure. Highly robust and self-sustaining.
* **Cons**: Slightly expands the list of auto-staged files, which is negligible.

### Recommendation
Option B is recommended to prevent future leakage of modified issue CLI files.

## Tasks
- [x] Add `.agents/scripts/cli/commands/issue.py` to `files_to_stage` in `issue.py`. <!-- id: subtask-issue-py-staging -->

## Acceptance Criteria
- [x] `.agents/scripts/cli/commands/issue.py` is present in `files_to_stage` in `issue.py`.
- [x] Validation suite passes.
