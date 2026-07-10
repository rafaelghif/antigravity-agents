---
id: issue-242
title: "fix: installer missing AGENTS.md root file copying"
status: closed
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
fix: installer missing AGENTS.md root file copying

## Tasks
- [x] Update install.sh to copy AGENTS.md <!-- id: task-install-sh -->
- [x] Update install.ps1 to copy AGENTS.md <!-- id: task-install-ps1 -->
- [x] Add parity tests in test_platform_drift.py <!-- id: task-parity-test -->

## Acceptance Criteria
- [x] install.sh successfully copies AGENTS.md during installation <!-- id: criteria-sh-copies -->
- [x] install.ps1 successfully copies AGENTS.md during installation <!-- id: criteria-ps1-copies -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] install.sh, install.ps1, .agents/tests/test_platform_drift.py <!-- id: audit-target-files -->
- Active module locks:
  - [x] install.sh, <!-- id: lock-install_sh, -->
  - [x] install.sh <!-- id: lock-install_sh -->
  - [x] install.ps1 <!-- id: lock-install_ps1 -->
  - [x] .agents/tests/test_platform_drift.py <!-- id: lock-test_platform_drift_py -->
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
