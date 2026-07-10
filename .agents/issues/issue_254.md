---
id: issue-254
title: "feat: implement modular schema grouping and strict on-demand loading checks"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
feat: implement modular schema grouping and strict on-demand loading checks

## Tasks
- [x] Update AGENTS.md to define modular schema directory layout under `.agents/schemas/` and strict on-demand loading guidelines <!-- id: task-update-agents-modular-schema -->
- [x] Update .agents/rules.md to synchronize modular schema guidelines for optimized context sizes <!-- id: task-update-rules-modular-schema -->
- [x] Enhance .agents/scripts/validate.py to programmatically check for matching modular schema updates under `.agents/schemas/` <!-- id: task-enhance-validate-modular -->
- [x] Run compliance validation and verify workspace integrity <!-- id: task-verify-modular-schema -->

## Acceptance Criteria
- [x] Modular schema design under `.agents/schemas/` is explicitly documented. <!-- id: criteria-schemas-docs -->
- [x] validate.py issues warnings if matching modular schemas are not updated when database files change. <!-- id: criteria-validation-check -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] None <!-- id: audit-target-files -->
- Active module locks:
  - [ ] validate <!-- id: lock-validate -->
  - [ ] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
