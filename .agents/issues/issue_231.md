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
- [x] Prevent install.sh from copying raw AGENTS.md to target project <!-- id: task-install-sh -->
- [x] Prevent install.ps1 from copying raw AGENTS.md to target project <!-- id: task-install-ps1 -->
- [x] Make bootstrap.sh version sync conditional on agent core repo <!-- id: task-boot-sh-sync -->
- [x] Make bootstrap.ps1 version sync conditional on agent core repo <!-- id: task-boot-ps1-sync -->
- [x] Update bootstrap.py to handle version sync dynamically for core repo <!-- id: task-boot-py-sync -->
- [x] Run full workspace validation and unit tests <!-- id: task-validate -->

## Acceptance Criteria
- [x] Freshly bootstrapped target projects start at 0.1.0 or detected version instead of agent version. <!-- id: criteria-fresh-ver -->
- [x] Agent core repository version is preserved and synchronizes correctly. <!-- id: criteria-core-ver -->
- [x] All unit tests pass successfully. <!-- id: criteria-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] install.sh <!-- id: audit-target-files -->
  - [x] install.ps1 <!-- id: audit-target-files-2 -->
  - [x] bootstrap.sh <!-- id: audit-target-files-3 -->
  - [x] bootstrap.ps1 <!-- id: audit-target-files-4 -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files-5 -->
  - [x] .agents/scripts/cli/commands/context.py <!-- id: audit-target-files-6 -->
- Active module locks:
  - [x] install <!-- id: lock-install -->
  - [x] bootstrap <!-- id: lock-bootstrap -->
  - [x] context <!-- id: lock-context -->
  - [x] list <!-- id: lock-list -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
