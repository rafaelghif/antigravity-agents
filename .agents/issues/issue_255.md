---
id: issue-255
title: "feat: implement cross-module schema dependency mapping and 10-year critical thinking guidelines"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
feat: implement cross-module schema dependency mapping and 10-year critical thinking guidelines

## Tasks
- [x] Update AGENTS.md to define modular schema dependencies and 10-year enterprise-grade critical thinking guidelines <!-- id: task-update-agents-critical -->
- [x] Update .agents/rules.md to synchronize modular database relationships and architectural foresight requirements <!-- id: task-update-rules-critical -->
- [x] Enhance .agents/scripts/validate.py codebase rule compliance checks to verify database model validation and foreign key cross-references <!-- id: task-enhance-validate-critical -->
- [x] Run compliance validation and verify workspace integrity <!-- id: task-verify-critical-standards -->

## Acceptance Criteria
- [x] Cross-module schema dependency mapping protocol (using references) is documented in AGENTS.md. <!-- id: criteria-dependency-mapping -->
- [x] 10-year software engineering/architectural foresight rules are added to AGENTS.md and rules.md. <!-- id: criteria-10year-foresight -->
- [x] validate.py checks that any modified database/schema file has its dependencies loaded or validated. <!-- id: criteria-validate-checks -->

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
