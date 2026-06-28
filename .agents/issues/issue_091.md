---
id: issue-091
title: "Implement unified API credentials, GPG diagnostics, PowerShell completion, and lock auto-pruning"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Implement unified API credentials configuration fallback, GPG diagnostics in the doctor subcommand, PowerShell autocomplete, and lock auto-pruning.

## Tasks
- [x] Task 1: Update git_api.py get_pat to read from git_profiles.json fallback
- [x] Task 2: Implement GPG key diagnostics check in doctor.py
- [x] Task 3: Add powershell support to completion.py
- [x] Task 4: Auto-prune locks in issue close flow
- [x] Task 5: Run tests and validate compliance

## Acceptance Criteria
- [x] Active profile's token is successfully used as fallback for GitHub API requests.
- [x] doctor command detects missing/expired GPG signing keys.
- [x] completion command supports PowerShell output successfully.
- [x] Module locks associated with the branch are auto-released on issue close before merge.
- [x] Validation checklist passes.
