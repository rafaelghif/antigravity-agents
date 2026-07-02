---
id: issue-124
title: "Improve release commit messages by injecting local issue titles and formatting Refs trailer"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Improve release commit messages by injecting local issue titles and formatting Refs trailer

## Tasks
- [x] Task 1: Modify issue.py close command to retrieve issue title and append to commit message
- [x] Task 2: Format the task trailer as Refs: issue-id in issue.py close command
- [x] Task 3: Verify and run validation tests

## Acceptance Criteria
- [x] Release commit messages contain the issue title (if available)
- [x] Release commit messages have a properly formatted Refs: issue-id body
- [x] Local tests pass successfully
