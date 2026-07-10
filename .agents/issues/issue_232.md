---
id: 232
title: "Fix Ubuntu installation and ensure full Git source updates"
status: closed
assignee: agent-antigravity
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
Fix Ubuntu installation and ensure full Git source updates

## Tasks
- [x] Update install.sh to overwrite existing core files during installation/upgrade <!-- id: task-install-sh -->
- [x] Update install.ps1 to overwrite existing core files during installation/upgrade <!-- id: task-install-ps1 -->
- [x] Run workspace validation and test installation <!-- id: task-validate -->

## Acceptance Criteria
- [x] install.sh overwrites existing files with latest Git source <!-- id: criteria-sh-overwrite -->
- [x] install.ps1 overwrites existing files with latest Git source <!-- id: criteria-ps1-overwrite -->
- [x] Validation checks pass successfully <!-- id: criteria-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] install.sh <!-- id: audit-target-files -->
  - [x] install.ps1 <!-- id: audit-target-files-2 -->
- Active module locks:
  - [x] install <!-- id: lock-install -->
  - [x] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
