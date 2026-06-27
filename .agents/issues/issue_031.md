---
id: issue-031
title: "Force non-fast-forward merges for strict branch tracking in Git history"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
When closing tasks, Git performs a fast-forward merge by default. This makes the commits appear linear, losing the branch tracking history in version control graphs (like VS Code Git Graph). We need to force a non-fast-forward merge (`--no-ff`) with a conventional commit message to ensure explicit tracking.

## Tasks
- [x] Implement `--no-ff` merge with conventional commit message in issue.py close action
- [x] Update unit tests in test_issue.py to match new merge arguments
- [x] Verify validations and run issue close command to merge and close issue-031

## Acceptance Criteria
- [x] Merges are executed using `--no-ff`
- [x] Merge commits use compliant conventional commit message: `chore(git): merge branch <branch_name>` with issue ID in body
- [x] Branch merges show up as explicit merge nodes in Git history
