---
id: issue-164
title: "Implement strict token budget tracker and logging CLI"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Implement strict token budget tracker and logging CLI

## Tasks
- [x] Update `.agents/issues/issue_164.md` subtasks and claim in board
- [x] Implement `token.py` CLI command module with log, status, and reset subcommands
- [x] Register `token` command in `helper.py`
- [x] Document token budget schema in `.agents/schema.md`
- [x] Document strict token tracking rules in `AGENTS.md` and `.agents/rules.md`
- [x] Add unit test suite `test_token.py` and run validate checks

## Acceptance Criteria
- [x] `./helper.sh token log <prompt> <completion> [--task <id>]` successfully updates `token_budget.json` and logs usage
- [x] `./helper.sh token status` displays correct token budgets, limits, and usage
- [x] CLI `token` command is registered and discoverable under `./helper.sh`
- [x] Unit tests for token budget tracking pass successfully
- [x] `./helper.sh validate` runs and passes successfully
