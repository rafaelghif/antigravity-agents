---
id: issue-124
title: "Improve release commit messages by injecting local issue titles and formatting Refs trailer"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Improve release commit messages by injecting local issue titles and formatting Refs trailer

## Tasks
- [ ] Task 1: Modify issue.py close command to retrieve issue title and append to commit message
- [ ] Task 2: Format the task trailer as Refs: issue-id in issue.py close command
- [ ] Task 3: Verify and run validation tests

## Acceptance Criteria
- [ ] Release commit messages contain the issue title (if available)
- [ ] Release commit messages have a properly formatted Refs: issue-id body
- [ ] Local tests pass successfully
