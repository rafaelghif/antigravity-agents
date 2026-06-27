---
id: issue-071
title: "Sync and resolve bugs in Windows scripts"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The installation, bootstrapping, and execution scripts for Antigravity Agent Core have several bugs and alignment differences on Windows (PowerShell) compared to Ubuntu/Unix (Bash), leading to issues when running in subdirectories, handling Windows-specific Python stubs, and executing direct local installations.

Key issues to fix:
1. **Python Executable Resolution**: `helper.ps1` and `bootstrap.ps1` run Python command stubs if present, which might be Windows Store stubs that hang or redirect. They should dynamically detect the real Python 3 executable.
2. **Directory Relative Execution**: Running `helper.ps1` and `helper.sh` from a subdirectory fails because they reference `./.agents/...` relatively. They should resolve path relative to the wrapper script's directory.
3. **Local Dev Bootstrap CWD Mismatch**: During local dev installation, `install.sh` and `install.ps1` execute the bootstrapper in the caller's working directory instead of the target installation directory.
4. **PowerShell Argument Splatting**: `helper.ps1` passes `$args` directly, which can cause string argument splitting/quoting issues. It should use splatting `@args` instead.
5. **Absolute Path Link Validation**: In `validate.py`, absolute link checks fail on Windows when resolved with a leading slash (e.g. `/C:/path`).

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Write OS-specific custom wrappers for each issue**
   - **Details**: Implement custom environment variable configurations and paths.
   - **Complexity**: High maintenance overhead.
   - **Downstream impact**: Hard to keep in parity as wrappers diverge further.
2. **Option B: Standardize wrapper script resolutions, Python selection, and CWD alignment**
   - **Details**: Implement script-relative path detection, unified Python executable probing, target-directory bootstrap execution, and separator-safe path checks in `validate.py`.
   - **Complexity**: Low. Direct, clean, and highly robust.
   - **Downstream impact**: Guarantees perfect cross-platform parity and reliability in monorepos.

### Recommendation
Option B is selected as it directly aligns with the `coding-standards` playbook, keeps scripts clean, and eliminates platform discrepancies.

## Tasks
- [x] Task 1: Fix CWD mismatch during local dev bootstrapping in `install.sh` and `install.ps1`.
- [x] Task 2: Implement robust Python 3 detection and script-relative helper execution in `helper.ps1` and `bootstrap.ps1`.
- [x] Task 3: Improve argument passing in `helper.ps1` using splatting `@args`.
- [x] Task 4: Fix script-relative helper script resolution in `helper.sh`.
- [x] Task 5: Handle Windows drive letters in absolute file link checks in `validate.py`.
- [x] Task 6: Validate all changes and run unit tests.

## Acceptance Criteria
- [x] Direct local installation to target folder correctly runs bootstrap in the target context.
- [x] Wrapper scripts (`helper.sh` and `helper.ps1`) work when invoked from subdirectories.
- [x] Python execution stubs on Windows do not block helper execution.
- [x] Windows file links (with drive letters) pass validation check.
- [x] Validation suite and all unit tests pass successfully.
