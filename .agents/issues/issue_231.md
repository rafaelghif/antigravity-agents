---
id: issue-231
title: "chore: unify V3 changelog entries and align version to 3.0.1"
status: open
assignee: rafaelghif
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
chore: unify V3 changelog entries and align version to 3.0.1

## Tasks
- [ ] Prevent install.sh from copying raw AGENTS.md to target project <!-- id: task-install-sh -->
- [ ] Prevent install.ps1 from copying raw AGENTS.md to target project <!-- id: task-install-ps1 -->
- [ ] Make bootstrap.sh version sync conditional on agent core repo <!-- id: task-boot-sh-sync -->
- [ ] Make bootstrap.ps1 version sync conditional on agent core repo <!-- id: task-boot-ps1-sync -->
- [ ] Update bootstrap.py to handle version sync dynamically for core repo <!-- id: task-boot-py-sync -->
- [ ] Run full workspace validation and unit tests <!-- id: task-validate -->

## Acceptance Criteria
- [ ] Freshly bootstrapped target projects start at 0.1.0 or detected version instead of agent version. <!-- id: criteria-fresh-ver -->
- [ ] Agent core repository version is preserved and synchronizes correctly. <!-- id: criteria-core-ver -->
- [ ] All unit tests pass successfully. <!-- id: criteria-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] install.sh <!-- id: audit-target-files -->
  - [ ] install.ps1 <!-- id: audit-target-files-2 -->
  - [ ] bootstrap.sh <!-- id: audit-target-files-3 -->
  - [ ] bootstrap.ps1 <!-- id: audit-target-files-4 -->
  - [ ] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files-5 -->
  - [ ] .agents/scripts/cli/commands/context.py <!-- id: audit-target-files-6 -->
- Active module locks:
  - [ ] install <!-- id: lock-install -->
  - [ ] bootstrap <!-- id: lock-bootstrap -->
  - [ ] context <!-- id: lock-context -->
  - [ ] list <!-- id: lock-list -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
