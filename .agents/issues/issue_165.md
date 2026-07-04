---
id: issue-165
title: "Support per-account token budget counters"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Support per-account token budget counters

## Tasks
- [x] Update `.agents/issues/issue_165.md` subtasks and claim in board
- [x] Implement active profile name auto-detection and per-account counting in `token.py`
- [x] Update token budget schema documentation in `.agents/schema.md`
- [x] Add unit tests for per-account token tracking in `test_token.py`
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] Token usage is logged per-account under the `"accounts"` key in `token_budget.json`
- [x] Status command shows per-account breakdown of daily, monthly, and total tokens
- [x] Unit tests for per-account token tracking pass successfully
- [x] `./helper.sh validate` passes successfully
