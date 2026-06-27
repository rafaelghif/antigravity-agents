---
id: issue-029
title: "Implement automated branch merge and board transition in issue close command"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The branch merge back to the base branch (main/master) and task board transitions are currently manual, which leads to flow drift. We need to automate this within the `issue close` CLI command to enforce strict compliance.

## Tasks
- [x] Implement automated validations, changelog, and board transitions in issue.py close action
- [x] Add branch merge and cleanup automation in issue.py close action
- [x] Add unit tests for the automated close and merge commands
- [x] Validate and merge the branch using the new issue close command

## Acceptance Criteria
- [x] `./helper.sh issue close issue-029` merges the branch to main and deletes it automatically
- [x] All unit tests pass and validations are clean
