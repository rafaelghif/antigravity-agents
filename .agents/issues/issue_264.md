---
id: issue-264
title: "pin dependencies in Dockerfile to prevent supply chain vulnerabilities"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
pin dependencies in Dockerfile to prevent supply chain vulnerabilities

## Tasks
- [x] pin python (black, flake8) and node (eslint) packages in Dockerfile <!-- id: task-1 -->

## Acceptance Criteria
- [x] validation passes and Dockerfile contains pinned dependencies <!-- id: criteria-1 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] Dockerfile <!-- id: audit-target-files -->
- Active module locks:
  - [ ] Dockerfile <!-- id: lock-Dockerfile -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
