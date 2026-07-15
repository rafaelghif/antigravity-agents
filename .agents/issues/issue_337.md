---
id: 337
title: "feat: standardize database schema registry and documentation protocol"
status: closed
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
feat: standardize database schema registry and documentation protocol

## Tasks
- [x] Integrate standard database schema registry and table formatting to .agents/schema.md <!-- id: task-standardize-schema-registry -->
- [x] Document database schema evolution and updates protocol in database-evolution skill <!-- id: task-document-db-evolution-protocol -->

## Acceptance Criteria
- [x] .agents/schema.md includes a standard database schema section and table layout template <!-- id: ac-schema-std -->
- [x] database-evolution playbook contains the schema sync protocol <!-- id: ac-db-evolution-proto -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/schema.md <!-- id: target-schema-md -->
  - [x] .agents/skills/database-evolution/SKILL.md <!-- id: target-database-evolution-skill -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
