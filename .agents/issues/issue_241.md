---
id: issue-241
title: "chore: sync installation scripts to copy Dockerfile"
status: closed
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
chore: sync installation scripts to copy Dockerfile

## Tasks
- [x] Update install.sh to copy Dockerfile <!-- id: task-install-sh -->
- [x] Update install.ps1 to copy Dockerfile <!-- id: task-install-ps1 -->

## Acceptance Criteria
- [x] install.sh successfully copies Dockerfile during installation <!-- id: criteria-sh-copies -->
- [x] install.ps1 successfully copies Dockerfile during installation <!-- id: criteria-ps1-copies -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] install.sh, install.ps1 <!-- id: audit-target-files -->
- Active module locks:
  - [x] install.sh, install.ps1 <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
