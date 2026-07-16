---
id: issue-355
title: "harden global leak prevention guidelines in workspace rules"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
harden global leak prevention guidelines in workspace rules

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Explicitly update the workspace-isolation guidelines in both active files (`AGENTS.md` and `.agents/rules.md`) and their template configurations to specify that no caching, credentials, or temporary files should ever be written to global/home folders, ensuring absolute workspace isolation.
- **Option B**: Maintain current rules as is. Less strict, higher risk of path leakages in future developments.

## Tasks
- [x] Task 1: Update workspace isolation guidelines in active files `AGENTS.md` and `.agents/rules.md`. <!-- id: task-update-active -->
- [x] Task 2: Update workspace isolation guidelines in templates `.agents/templates/AGENTS.md.template` and `.agents/templates/rules.md.template`. <!-- id: task-update-templates -->
- [x] Task 3: Verify template-to-target parity and run local validations. <!-- id: task-validate -->

## Acceptance Criteria
- [x] Active rules and templates contain the strict guidelines against global folder leakage. <!-- id: ac-harden-rules -->
- [x] `./helper.sh validate` runs and completes successfully. <!-- id: ac-validate -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `AGENTS.md` <!-- id: target-agents -->
  - [x] `.agents/rules.md` <!-- id: target-rules -->
  - [x] `.agents/templates/AGENTS.md.template` <!-- id: target-agents-template -->
  - [x] `.agents/templates/rules.md.template` <!-- id: target-rules-template -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
