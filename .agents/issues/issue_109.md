---
id: issue-109
title: "Optimize validation guard performance and decouple remote sync"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Optimize validation guard performance and decouple remote sync

## Tasks
- [x] Decouple issue_cmd.sync_issues() from validate.py
- [x] Optimize prune_stale_locks() in validate.py to use single subprocess call
- [x] Add .agents/logs/ to .antigravityignore
- [x] Verify validations pass and close task

## Acceptance Criteria
- [x] validate.py runs successfully and does not automatically query GitHub issues or write issue files.
- [x] prune_stale_locks() queries refs in a single execution.
- [x] .agents/logs/ is ignored by antigravity CLI.
