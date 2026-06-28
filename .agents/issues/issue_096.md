---
id: issue-096
title: "Fix parameter parsing error in bootstrap.ps1 on Windows"
status: open
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Fix parameter parsing error in bootstrap.ps1 on Windows

## Tasks
- [x] Fix Test-Path parameter binding issue in bootstrap.ps1 by wrapping in parentheses
- [x] Verify local validation checks pass

## Acceptance Criteria
- [x] bootstrap.ps1 is syntax error free in PowerShell and executes properly
