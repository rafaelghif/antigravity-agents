---
id: issue-243
title: "feat: bypass git hooks for non-agent commits"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The current local git hooks (pre-commit, commit-msg, prepare-commit-msg) enforce very strict compliance checks, which prevent the human programmer from committing and coding freely unless they structure every commit exactly like the agent is required to. The rules (like Conventional Commits, Task ID references, Compliance Audit headers) should only restrict the AI agent, not the programmer.

## Tasks
- [x] Update git hook template definitions in `.agents/scripts/validate.py` to bypass execution if `ANTIGRAVITY_AGENT` is not set. <!-- id: task-validate-py-hooks -->
- [x] Update git hook template definitions in `.agents/scripts/cli/commands/doctor.py` to bypass execution if `ANTIGRAVITY_AGENT` is not set. <!-- id: task-doctor-py-hooks -->
- [ ] Run validation or doctor to repair hooks and verify that `ANTIGRAVITY_AGENT` environment variable checks are present in actual hooks. <!-- id: task-repair-hooks -->
- [ ] Run unit tests and run project validate to verify all changes. <!-- id: task-run-tests-validation -->

## Acceptance Criteria
- [ ] Local git hooks bypass validation and exit with 0 immediately when `ANTIGRAVITY_AGENT` is not set. <!-- id: criteria-bypass-non-agent -->
- [ ] Local git hooks still enforce all validation checks when `ANTIGRAVITY_AGENT` is set. <!-- id: criteria-enforce-agent -->
- [ ] Diagnostics run successfully and unit tests pass. <!-- id: criteria-diagnostics-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/cli/commands/doctor.py`
- Active module locks:
  - [ ] .agents/scripts/cli/commands/doctor <!-- id: lock-doctor -->
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
