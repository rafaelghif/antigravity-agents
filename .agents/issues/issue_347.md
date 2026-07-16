---
id: issue-347
title: "Audit and refactor installer and bootstrapper for safety and path correctness"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
The bootstraping and installation scripts need to be verified to ensure they copy all files in `.agents/scripts/core` correctly, resolve python import paths cleanly without global/parent namespace collision, and utilize the safe `ShellExecutor` and `StructuredLogger` where applicable.

## Tasks
- [x] Check bootstrap and install script logic for core path parity <!-- id: task-check-parity -->
- [x] Refactor bootstrap.py and install.py subprocess and print calls to use executor and logger <!-- id: task-refactor-calls -->
- [x] Validate and sync all changes <!-- id: task-validate-sync -->

## Acceptance Criteria
- [x] Bootstrap and install routines successfully complete validation <!-- id: ac-validation -->
- [x] Correct core parent path resolution without import warnings <!-- id: ac-import-resolution -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/cli/commands/bootstrap.py` <!-- id: target-bootstrap -->
  - [x] `.agents/scripts/cli/commands/install.py` <!-- id: target-install -->
- Active module locks:
  - [x] bootstrap.py locked <!-- id: audit-lock-bootstrap -->
  - [x] install.py locked <!-- id: audit-lock-install -->
