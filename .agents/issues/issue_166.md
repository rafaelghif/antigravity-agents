---
id: issue-166
title: "Track token budget per API key or active API account"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Track token budget per API key or active API account

## Tasks
- [x] Update `.agents/issues/issue_166.md` subtasks and claim in board
- [x] Implement secure API key masking and active API profile detection in `token.py`
- [x] Update token budget schema documentation in `.agents/schema.md`
- [x] Add unit tests for API key/account-based token tracking in `test_token.py`
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] Token usage is logged per API key or active API account name under the `"accounts"` key in `token_budget.json`
- [x] Token status breakdown displays the masked API key or active API account name
- [x] Unit tests pass successfully
- [x] `./helper.sh validate` passes successfully
