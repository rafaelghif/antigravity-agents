---
id: issue-319
title: "docs: add prominent disclaimer of liability to readme to protect author liability"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Since the author shares this codebase with others, there is a risk of legal liability if a user's local workspace coding agent executes destructive operations or leaks keys. A clear, professional legal warning and liability disclaimer block must be added prominently at the top of the README.md to protect the author.

## Tasks
- [x] Move issue-319 to Doing in task board <!-- id: task-move-board -->
- [x] Add disclaimer of liability warning block to README.md under the main intro block <!-- id: task-edit-readme -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] README.md contains a clear disclaimer block explaining that the software is provided "as is" and the author has no liability for agent actions. <!-- id: ac-disclaimer-added -->
- [x] All workspace validations pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] README.md <!-- id: audit-target-readme -->
  - [x] .agents/issues/issue_319.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] readme <!-- id: lock-readme -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
