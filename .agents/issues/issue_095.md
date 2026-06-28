---
id: issue-095
title: "Enhance CLI interactive UX and remove Web Dashboard"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Enhance CLI interactive UX and remove Web Dashboard

## Tasks
- [x] Remove local web dashboard command module ui.py and delete vscode-extension directory
- [x] Remove ui command references from helper CLI and main instructions
- [x] Implement generic interactive arrow-key selection utility with standard TTY raw mode and Windows fallback
- [x] Integrate interactive selection in profile switch if profile name is omitted
- [x] Integrate interactive selection in issue checkout and close if issue ID is omitted
- [x] Integrate interactive prompt in issue create if title is omitted
- [x] Integrate interactive selection in lock and unlock if module name is omitted

## Acceptance Criteria
- [x] CLI execution works correctly without importing or calling deleted ui module
- [x] Interactive prompts fall back gracefully in non-TTY environments
- [x] Validation tests pass successfully
