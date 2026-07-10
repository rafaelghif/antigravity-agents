---
id: issue-242
title: "fix: installer missing AGENTS.md root file copying"
status: open
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
- [x] Update bootstrap.py to copy missing core directories and files <!-- id: task-bootstrap-dirs-files -->
- [x] Update test_bootstrap.py to mock copying and assert existence <!-- id: task-test-bootstrap -->
- [x] Update install.sh to copy bootstrap.sh and bootstrap.ps1 <!-- id: task-install-sh-bootstrap -->
- [x] Update install.ps1 to copy bootstrap.sh and bootstrap.ps1 <!-- id: task-install-ps1-bootstrap -->
- [x] Update bootstrap.py to copy bootstrap.sh and bootstrap.ps1 <!-- id: task-bootstrap-py-bootstrap -->
- [x] Update test_platform_drift.py expected files list <!-- id: task-drift-expected -->
- [x] Update test_bootstrap.py expected files list and assertions <!-- id: task-test-bootstrap-expected -->
- [x] Deduplicate .agents/rules.md to optimize AI Agent prompt footprint and focus <!-- id: task-dedup-rules -->
- [x] Lock rules.md for verification and audit compliance <!-- id: task-lock-rules -->

## Acceptance Criteria
- [x] install.sh successfully copies AGENTS.md during installation <!-- id: criteria-sh-copies -->
- [x] install.ps1 successfully copies AGENTS.md during installation <!-- id: criteria-ps1-copies -->
- [x] bootstrap.py successfully copies docs, dashboard, Dockerfile, and projects.example <!-- id: criteria-bootstrap-copies -->
- [x] install.sh copies bootstrap.sh and bootstrap.ps1 <!-- id: criteria-sh-bootstrap -->
- [x] install.ps1 copies bootstrap.sh and bootstrap.ps1 <!-- id: criteria-ps1-bootstrap -->
- [x] bootstrap.py copies bootstrap.sh and bootstrap.ps1 <!-- id: criteria-bootstrap-py-bootstrap -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] install.sh, install.ps1, .agents/tests/test_platform_drift.py, .agents/scripts/cli/commands/bootstrap.py, .agents/tests/test_bootstrap.py, .agents/rules.md <!-- id: audit-target-files -->
- Active module locks:
  - [x] install.sh, <!-- id: lock-install_sh, -->
  - [x] install.sh <!-- id: lock-install_sh -->
  - [x] install.ps1 <!-- id: lock-install_ps1 -->
  - [x] .agents/tests/test_platform_drift.py <!-- id: lock-test_platform_drift_py -->
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/rules.md <!-- id: lock-rules_md -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
