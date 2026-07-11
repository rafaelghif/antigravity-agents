---
id: issue-291
title: "Verify and harden dummy installation plug and play consistency"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The user reported inconsistencies during dummy installation and requested that the agent workspace setup be fully plug-and-play. We need to:
1. Run a dummy installation in a temporary directory.
2. Compare the installed files one-by-one with the repository templates and core files.
3. Identify and fix any missing files, configuration mismatches, or platform drift in `install.sh`, `install.ps1`, `bootstrap.sh`, `bootstrap.ps1`, and `bootstrap.py`.
4. Ensure the bootstrapper runs non-interactively without blocking.

## Tasks
- [x] Implement non-interactive quick mode fallback in `bootstrap.py` when standard input is not a TTY <!-- id: task-bootstrap-noninteractive -->
- [x] Align extra arguments passing between `install.sh` and `install.ps1` for bootstrap wrapping <!-- id: task-align-installers -->
- [x] Run dummy installation and compare files one-by-one to check consistency <!-- id: task-compare-install -->
- [x] Fix any found file discrepancies or configuration mismatches <!-- id: task-fix-mismatches -->
- [x] Verify validation passes cleanly and close the issue <!-- id: task-validate-close -->

## Acceptance Criteria
- [x] Installation succeeds without blocking on interactive prompts in non-interactive shell. <!-- id: ac-noninteractive-success -->
- [x] File-by-file comparison shows absolute parity and consistency between source templates/core and installed targets. <!-- id: ac-install-parity -->
- [x] Unit tests and validations pass. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-bootstrap-file -->
  - [x] install.sh <!-- id: audit-install-sh -->
  - [x] install.ps1 <!-- id: audit-install-ps1 -->
- Active module locks:
  - [ ] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
