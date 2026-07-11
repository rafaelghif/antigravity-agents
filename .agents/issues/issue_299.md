---
id: issue-299
title: "Unify Shell Wrapper Parsing and Setup Logic within Python Core"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Consolidate platform-specific installer and bootstrapper shell script wrapper logic into a unified, platform-agnostic Python implementation. This eliminates platform-drift and script duplication, making the shell files thin delegates.

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Implement all folder copying, backups, hooks setup, and template copies natively in Python (`install.py` and `bootstrap.py`). The shell wrappers become thin delegates that check dependencies and call Python.
  - *Pros*: Natively cross-platform (zero dependency on `robocopy`, `find`, or `cp`), type-safe, unified source of truth, easy to unit-test.
  - *Cons*: Requires Python to be present prior to copying code (the shell wrapper checks this and clones to a temp dir first, which is standard).
- **Option B**: Keep shell scripts doing heavy copy lifting, but add more parity validations in `validate.py`.
  - *Pros*: Shell scripts remain standalone.
  - *Cons*: High duplication between bash and powershell, platform drift risk, hard to maintain.

*Recommendation*: Proceed with Option A.

## Tasks
- [ ] Task 1: Map the new 'install' command in helper.py and create the install.py skeleton <!-- id: task-install-skeleton -->
- [ ] Task 2: Implement target directory verification, automated backups, and recursive file copies in install.py <!-- id: task-install-copy-logic -->
- [ ] Task 3: Migrate directory creation, templates copying, version syncing, and hooks setup into bootstrap.py <!-- id: task-bootstrap-setup -->
- [ ] Task 4: Refactor install.sh/install.ps1 to perform only minimum checks and call install.py <!-- id: task-install-wrappers -->
- [ ] Task 5: Refactor bootstrap.sh/bootstrap.ps1 to thin-delegate to bootstrap.py <!-- id: task-bootstrap-wrappers -->
- [ ] Task 6: Add unit tests for the new install command and bootstrap setups <!-- id: task-unit-tests -->
- [ ] Task 7: Run validation guard checks and finalize merge <!-- id: task-validation-final -->

## Acceptance Criteria
- [ ] Subprocess installers check python/git prerequisites and delegate copying to Python. <!-- id: ac-thin-wrappers -->
- [ ] Exclusions matches template-map/git-ignores and installs cleanly on both Unix and Windows. <!-- id: ac-clean-copy -->
- [ ] All 218+ unit tests pass. <!-- id: ac-unit-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/helper.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files-2 -->
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-files-3 -->
  - [x] install.sh <!-- id: audit-target-files-4 -->
  - [x] install.ps1 <!-- id: audit-target-files-5 -->
  - [x] bootstrap.sh <!-- id: audit-target-files-6 -->
  - [x] bootstrap.ps1 <!-- id: audit-target-files-7 -->
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files-8 -->
- Active module locks:
  - [ ] .agents/scripts/cli/helper <!-- id: lock-helper -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
  - [ ] .agents/scripts/cli/commands/install <!-- id: lock-install -->
  - [ ] .agents/tests/test_platform_drift <!-- id: lock-test_platform_drift -->
  - [ ] .agents/tests/test_install <!-- id: lock-test_install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
