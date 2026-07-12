---
id: issue-327
title: "fix: prevent install from scaffolding directory structures and project files"
status: open
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
The installer (`install.py`) runs the bootstrapper script (`bootstrap.py`) in target directories to initialize configuration files and templates. However, the bootstrapper automatically scaffolds a directory structure (such as Python's `src/core/entities` or Node's `src/api`) and writes language-specific configuration files (`requirements.txt`, `package.json`, `composer.json`) when it runs. This interferes with existing projects (polluting them with unwanted `src` directories and configuration overrides).
We need to:
1. Support a `--no-scaffold` flag in `.agents/scripts/cli/commands/bootstrap.py` to skip project scaffolding (folder structures, dependencies lists, schemas).
2. Pass `--no-scaffold` to the bootstrap command inside `.agents/scripts/cli/commands/install.py`.
3. Verify that running `install` or upgrading the agent does not scaffold directory structures or project files.

## Tasks
- [x] Add the `--no-scaffold` option parsing to `bootstrap.py` and skip directory structure scaffolding and config file generation if set. <!-- id: task-bootstrap-flag -->
- [x] Append `--no-scaffold` to the bootstrap call arguments in `install.py`. <!-- id: task-install-flag -->
- [x] Update unit tests in `test_bootstrap.py` to cover the `--no-scaffold` flag behavior. <!-- id: task-update-tests -->
- [x] Run validation checks to ensure tests and compliance pass successfully. <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Scaffolding (creation of `src/` directories and language manifests like `requirements.txt`) is completely skipped when `--no-scaffold` is passed. <!-- id: crit-no-scaffold-skip -->
- [x] Installer calls bootstrap with `--no-scaffold`. <!-- id: crit-install-uses-flag -->
- [x] Validation check passes successfully. <!-- id: crit-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/install.py
  - [x] .agents/tests/test_bootstrap.py
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: audit-module-locks -->
  - [x] .agents/scripts/cli/commands/install
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
