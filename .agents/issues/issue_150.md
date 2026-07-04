---
id: issue-150
title: "Implement comprehensive architectural and dashboard hardening"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Implement comprehensive architectural and dashboard hardening to solve background upgrade security risks, dashboard exposure vulnerabilities, task validation rigidity, and locks merge conflicts.

## Tasks
- [x] Harden auto-upgrade behavior to only check for updates and alert the user (never checkout in background)
- [x] Restrict dashboard HTTP server access strictly to localhost/loopback interfaces
- [x] Make checklist validation flexible by supporting optional tasks and interactive prompt overrides for humans
- [x] Untrack and git-ignore locks.json to prevent merge conflicts
- [x] Verification complete

## Acceptance Criteria
- [x] Background thread only alerts available upgrades and never checks out code automatically
- [x] External/LAN requests to the dashboard are blocked with 403 Forbidden
- [x] Optional tasks (`(optional)`) are skipped in validation, and interactive validation allows override
- [x] Locks checking is local, shared, and locks.json is git-ignored and untracked
- [x] All unit tests and validation checks pass successfully
