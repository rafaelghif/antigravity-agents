---
id: issue-293
title: "Clean up archived issue files from active tracking directory"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
There are 23 deleted issue specification files in the working directory that represent closed/archived issues (from issue 266 to 289). They are already archived and closed, so they are no longer needed in the active `.agents/issues/` directory. We need to stage these deletions and commit them.

## Tasks
- [x] Stage the deletion of the 23 closed issue files <!-- id: task-stage-deletions -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] The 23 closed issue files are removed from Git. <!-- id: ac-files-deleted -->
- [x] Validation checks pass cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/issues/ <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
