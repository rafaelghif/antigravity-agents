---
id: issue-188
title: "Self heal active context and enhance CLI DX"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Self heal active context and enhance CLI DX

## Tasks
- [x] Implement self-healing active context manifest regeneration on validation guard startup <!-- id: task-validate-heal -->
- [x] Trigger context optimization automatically after checkout subcommand in issue.py <!-- id: task-checkout-heal -->

## Acceptance Criteria
- [x] Validation guard regenerates active_context.md if missing.
- [x] Checking out an issue via CLI automatically updates active_context.md.
