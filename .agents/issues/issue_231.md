---
id: 231
title: "Fix Windows installations failing"
status: open
assignee: agent-antigravity
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
Fix Windows installations failing

## Tasks
- [x] Update install.ps1 to support local dev mode and temporarily disable strict error action preference during native commands <!-- id: task-install-ps1 -->
- [x] Update bootstrap.ps1 to temporarily disable strict error action preference during native git commands <!-- id: task-bootstrap-ps1 -->
- [ ] Run workspace validation and test installation <!-- id: task-validate -->

## Acceptance Criteria
- [ ] install.ps1 runs successfully without NativeCommandError on Windows <!-- id: criteria-no-native-error -->
- [ ] LocalDev mode works when env variable is set <!-- id: criteria-local-dev -->
- [ ] Validation guard checks pass <!-- id: criteria-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] install.ps1 <!-- id: audit-target-files -->
  - [ ] bootstrap.ps1 <!-- id: audit-target-files-2 -->
- Active module locks:
  - [ ] install <!-- id: lock-install -->
  - [ ] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
