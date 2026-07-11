---
id: issue-300
title: "Test Unified Installer on Clean Target and Update README"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Test the refactored installation wrapper scripts and Python logic on a clean target directory, do a one-on-one file comparison check, and update the README.md with unified requirements and architectural flow details.

## Tasks
- [x] Task 1: Execute installer in a clean sandbox folder targeting the local repository <!-- id: task-run-installer -->
- [x] Task 2: Perform a one-on-one file comparison check between source and installed target <!-- id: task-compare-files -->
- [x] Task 3: Update README.md with revised requirements, features, and setup instructions <!-- id: task-update-readme -->
- [x] Task 4: Run validation suite and verify compliance <!-- id: task-validate-compliance -->

## Acceptance Criteria
- [x] Refactored installer functions correctly on clean project target. <!-- id: ac-installer-success -->
- [x] Target folder files match source files exactly (excluding ignored/unwanted patterns). <!-- id: ac-folder-parity -->
- [x] README.md reflects correct version, requirements, and installation flow description. <!-- id: ac-readme-up-to-date -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] README.md <!-- id: audit-target-files -->
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files-2 -->
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
