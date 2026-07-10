---
id: issue-250
title: "feat: implement solo workflow mode and commit diff preview"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Implement two crucial programmer-facing DX features:
1. Solo Workflow Mode: skip dirty-checks on main branch when workflow_mode is set to "solo" in .agents/config.json.
2. Commit Diff Preview: show git diff --cached in color inside run_interactive_commit.

## Tasks
- [x] Integrate git diff --cached color preview in `commit.py`. <!-- id: task-commit-diff -->
- [x] Read config.json and bypass base branch validation when workflow_mode is "solo" in `validate.py`. <!-- id: task-solo-workflow -->

## Acceptance Criteria
- [x] Commit helper prints staged changes before prompting. <!-- id: criteria-commit-diff -->
- [x] Validation passes on main branch when configured for solo mode. <!-- id: criteria-solo-workflow -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/cli/commands/commit.py`
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
  - [x] .agents/scripts/cli/commands/commit <!-- id: lock-commit -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
