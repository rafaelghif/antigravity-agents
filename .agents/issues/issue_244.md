---
id: issue-244
title: "feat: improve DX by bypassing strict rules for human programmer and adding agent safety limits"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The developer requested to relax agent guardrails (specifically points 1, 2, 3, and 5) while preserving automated git commits (point 4) with strict agent safety checks. The goals are:
1. Bypass validation gates entirely for human developers (where `ANTIGRAVITY_AGENT != 1`).
2. Add `.lock/` transient locks folder to git ignores.
3. Automatically bypass module lock verification checks for humans.
4. Integrate a budget-based auto-merge safety barrier so the agent halts and lists manual git instructions if token limits are exceeded.

## Tasks
- [x] Integrate `ANTIGRAVITY_AGENT != "1"` check in `validate.py` to bypass execution for human developers. <!-- id: task-validate-bypass -->
- [x] Ignore `.lock/` transient directories in `.gitignore` and `.antigravityignore`. <!-- id: task-ignore-lock-dirs -->
- [x] Add token budget threshold guard (90% limit check) in `issue.py` close handler to bypass auto-merge/delete when limit is near. <!-- id: task-budget-safety -->
- [x] Run unit tests and verify workspace compliance. <!-- id: task-verify -->

## Acceptance Criteria
- [x] Human developer runs of `validate.py` immediately print a bypass message and exit with 0. <!-- id: criteria-human-bypass -->
- [x] All transient lock folders are ignored in git. <!-- id: criteria-ignored-lock -->
- [x] Automated git merges/branch deletions are bypassed with a clear warning and instructions if token limits are close/exceeded. <!-- id: criteria-auto-merge-limit -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/cli/commands/issue.py`
  - [x] `.gitignore`
  - [x] `.antigravityignore`
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
  - [x] .agents/scripts/cli/commands/issue <!-- id: lock-issue -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
