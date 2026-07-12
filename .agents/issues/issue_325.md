---
id: issue-325
title: "fix: prevent test pollution of src directory and exclude src from installer"
status: closed
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
The empty `src/presentation` folder is created at the repository root by the wrapper integration test. This creates pollution in the workspace root, which might interfere with or confuse developers in managed/target projects. We need to:
1. Shift the integration test's temporary directory to a git-ignored folder under `.agents/state/test_subdir`.
2. Implement strict cleanup in the integration test so that it removes the temporary test directory after running.
3. Explicitly exclude any `src` root folder in the installer (`install.py`) so that the agent core installation process never copies or tampers with the `src` folder of managed projects.
4. Remove the empty `src/presentation` and `src/` directories from the active workspace.

## Tasks
- [x] Update `test_helper_sh_relative_subdirectory_execution` in `.agents/tests/test_integration_wrappers.py` to use `.agents/state/test_subdir` and clean up via `shutil.rmtree`. <!-- id: task-update-test -->
- [x] Update `should_exclude` in `.agents/scripts/cli/commands/install.py` to ignore the `src/` folder. <!-- id: task-update-installer -->
- [x] Remove the empty `src/presentation` and `src` directories from the filesystem. <!-- id: task-remove-src -->
- [x] Run validation checks to ensure tests and rules pass cleanly. <!-- id: task-validate -->

## Acceptance Criteria
- [x] No `src/` directory is created in the repository root when running unit tests. <!-- id: crit-no-src-creation -->
- [x] The installer explicitly ignores the `src/` folder during installation recursively. <!-- id: crit-installer-ignores-src -->
- [x] Validation check passes successfully. <!-- id: crit-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tests/test_integration_wrappers.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/install.py
- Active module locks:
  - [x] core <!-- id: audit-module-locks -->
  - [x] rules
  - [x] .agents/scripts/cli/commands/install
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
