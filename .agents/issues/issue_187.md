---
id: issue-187
title: "Fix subtask deadlock and staging locks in CLI"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Fix subtask deadlock and staging locks in CLI

## Tasks
- [ ] Allow intermediate commits to pass branch alignment subtask check unless AAC_ENFORCE_SUBTASKS is set <!-- id: task-deadlock -->
- [ ] Remove locks.json from files_to_stage in issue close subcommand <!-- id: task-locks -->
- [ ] Add locks.json to .antigravityignore file <!-- id: task-ignore -->

## Acceptance Criteria
- [ ] The validation guard passes intermediate commits when subtasks are incomplete.
- [ ] Staging and merge execution does not stage or commit locks.json.
