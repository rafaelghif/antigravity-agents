---
id: issue-320
title: "fix: suppress git clone stderr NativeCommandError in install.ps1"
status: open
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
The Windows installer script `install.ps1` fails when cloning the remote repository because PowerShell treats output on standard error (stderr) from `git clone` as a terminating `NativeCommandError` under `$ErrorActionPreference = "Stop"`.

## Tasks
- [x] Implement Pre-Implementation Impact Analysis and Compliance Audit <!-- id: task-analysis -->
- [x] Update `install.ps1` to temporarily set ErrorActionPreference and use `--quiet` flag in `git clone` <!-- id: task-update-install-ps1 -->
- [ ] Verify installer execution by running a local dry run <!-- id: task-verify-installer -->

## Acceptance Criteria
- [ ] `install.ps1` runs successfully without raising `NativeCommandError` during git clone.
- [ ] `install.ps1` detects clone failures and prints an appropriate error.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] [install.ps1](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/install.ps1) <!-- id: audit-target-files -->
- Active module locks:
  - [x] 'install.ps1' <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
