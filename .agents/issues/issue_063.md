---
id: issue-063
title: "Commit README installation command updates"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The changes to `README.md` made in `issue-062` were not committed to the feature branch because `README.md` is not present in the `files_to_stage` list in `.agents/scripts/cli/commands/issue.py`'s `close` action. We need to commit `README.md` changes safely and also add it to `files_to_stage` to prevent future regressions.

## Pre-Implementation Impact Analysis

### Option A: Just commit README.md manually / via issue-063
* **Pros**: Simple, minimal code impact.
* **Cons**: Does not prevent future issues where a developer/agent modifies `README.md` but forgets to manually stage it before running `./helper.sh issue close`.

### Option B: Add README.md to files_to_stage list in issue.py (Recommended)
```python
files_to_stage = [
    path,
    ".agents/tasks/board.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "bootstrap.sh",
    "bootstrap.ps1",
    ".agents/scripts/cli/commands/bootstrap.py",
    "README.md"
]
```
* **Pros**: Ensures that updates to `README.md` are automatically staged and committed on issue close, avoiding uncommitted files leakage.
* **Cons**: Marginally increases the number of auto-staged files, but `README.md` is a core file that should always be tracked on release.

### Recommendation
Option B is highly recommended to improve developer experience and avoid uncommitted file leakage in future tasks.

## Tasks
- [x] Add `README.md` to `files_to_stage` in `.agents/scripts/cli/commands/issue.py`. <!-- id: subtask-issue-py-update -->

## Acceptance Criteria
- [x] `README.md` is present in `files_to_stage` in `issue.py`.
- [x] Validation suite passes.
