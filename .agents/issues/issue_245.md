---
id: issue-245
title: "feat: implement interactive commit helper, clear-all locks, default token status, and flexible branch validation"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Implement various developer experience (DX) improvements for the human programmer, including:
1. Conventional Commits helper via `git commit --interactive` / `commit -i`.
2. Clean all/prune locks subcommand in `helper.sh lock`.
3. Default `helper.sh token` subcommand to `status` to show token usage instantly.
4. Auto-generate temporary task MD files in `validate.py` on non-aligned branches to ensure flexible branch validation and zero crashes.

## Tasks
- [x] Integrate interactive commit builder in `commit.py`. <!-- id: task-commit-helper -->
- [x] Add `--clear` and `--prune` subcommands in `lock.py`. <!-- id: task-lock-features -->
- [x] Default `token.py` run function to show status if no subcommand is passed. <!-- id: task-token-default -->
- [x] Allow ad-hoc branch naming in `validate.py` by auto-generating task specification files. <!-- id: task-branch-flexibility -->
- [x] Run unit tests and verify workspace compliance. <!-- id: task-verify-tests -->

## Acceptance Criteria
- [x] Commits can be built interactively using `helper.py commit -i`. <!-- id: criteria-interactive-commit -->
- [x] Locks can be cleared using `--clear` and pruned using `--prune`. <!-- id: criteria-lock-cleanup -->
- [x] Running `./helper.sh token` with no args displays the token status dashboard. <!-- id: criteria-token-status -->
- [x] Non-standard branches auto-generate task files instead of failing validation checks. <!-- id: criteria-branch-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/cli/commands/commit.py`
  - [x] `.agents/scripts/cli/commands/lock.py`
  - [x] `.agents/scripts/cli/commands/token.py`
  - [x] `.agents/tests/test_validate.py`
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
  - [x] .agents/scripts/cli/commands/commit <!-- id: lock-commit -->
  - [x] .agents/scripts/cli/commands/lock <!-- id: lock-lock -->
  - [x] .agents/scripts/cli/commands/token <!-- id: lock-token -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
