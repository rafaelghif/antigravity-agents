---
id: issue-117
title: "Ignore active context archive directory in gitignore"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Ignore active context archive directory in gitignore

## Tasks
- [x] Add .agents/archive/ directory to .gitignore
- [x] Verify validations pass and close task

## Acceptance Criteria
- [x] .gitignore ignores .agents/archive/ folder completely.
- [x] git status does not show .agents/archive/ as untracked file.
- [x] Local validation guard passes cleanly.
