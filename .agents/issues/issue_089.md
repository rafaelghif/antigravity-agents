---
id: issue-089
title: "Synchronize and fix Linux and Windows installation and bootstrap scripts"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Synchronize, review, and fix bugs/gaps in Linux (install.sh, bootstrap.sh) and Windows (install.ps1, bootstrap.ps1) installation and bootstrap scripts to ensure consistency, robust Git hook creation in subdirectories/monorepos, safe Python executable detection, and correct file backup operations.

## Tasks
- [x] Task 1: Fix strict-mode property access bug in Windows installer backup step
- [x] Task 2: Implement robust Git repository hook destination detection using git-rev-parse
- [x] Task 3: Resolve python path detection discrepancies and enforce consistency in scripts
- [x] Task 4: Standardize folder extraction array/object parsing in Windows ZIP extractor
- [x] Task 5: Run tests and validation checks to verify correctness

## Acceptance Criteria
- [x] Windows and Linux install/bootstrap scripts must run without errors.
- [x] Git hooks must be successfully installed even if run in a monorepo subdirectory.
- [x] No strict-mode property lookup failures in PowerShell.
- [x] Validation checklist passes successfully.
