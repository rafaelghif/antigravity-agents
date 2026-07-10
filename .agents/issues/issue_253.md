---
id: issue-253
title: "feat: enforce strict workspace isolation and automated database schema memory documentation"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
feat: enforce strict workspace isolation and automated database schema memory documentation

## Tasks
- [x] Update AGENTS.md to enforce strict database/table schema tracking and prohibit leakage of configs/plans to global directories <!-- id: task-update-agents-rules -->
- [ ] Update .agents/rules.md to synchronize the database schema and workspace isolation rules <!-- id: task-update-rules-md -->
- [ ] Run verification tests and validation checks to verify workspace compliance <!-- id: task-verify-compliance -->

## Acceptance Criteria
- [ ] Database schema changes and discussions are explicitly mandated to be recorded in `.agents/schema.md`. <!-- id: criteria-schema-tracking -->
- [ ] Workspace-level isolation is explicitly enforced, forbidding any global leakages or writing to global configuration directories. <!-- id: criteria-workspace-isolation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] None <!-- id: audit-target-files -->
- Active module locks:
  - [ ] bootstrap <!-- id: lock-bootstrap -->
  - [ ] validate <!-- id: lock-validate -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
