---
id: issue-212
title: "Integrate interactive setup wizard launch into bootstrap scripts"
status: open
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to trigger the python bootstrap wizard command automatically inside `bootstrap.sh` and `bootstrap.ps1` to align setup prompting during installer setup on Windows and Linux.

## Tasks
- [x] Update `bootstrap.sh` to call `helper.py bootstrap` with argument forwarding <!-- id: task-update-bootstrap-sh -->
- [x] Update `bootstrap.ps1` to call `helper.py bootstrap` with argument forwarding <!-- id: task-update-bootstrap-ps1 -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Running `./bootstrap.sh` runs the python bootstrap wizard with any input arguments.
- [x] Running `.\bootstrap.ps1` runs the python bootstrap wizard with any input arguments.
- [x] Validation guard passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [bootstrap.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/bootstrap.sh)
  - [bootstrap.ps1](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/bootstrap.ps1)
- Active module locks:
  - None
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
