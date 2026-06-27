---
id: issue-070
title: "Fix PowerShell hooks directory resolution path mismatch"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
During Windows installation/bootstrapping, `bootstrap.ps1` uses `.NET` `[System.IO.Path]::GetFullPath` to resolve hook destination paths. In PowerShell, the `.NET` working directory remains at the initial process launching directory (typically the user's home folder, e.g. `C:\Users\Muraghi`), whereas `Get-Location` represents the active project context path. Since `C:\Users\Muraghi` happened to contain a `.git` folder, `Test-Path ".git"` evaluated to true, but the script then attempted to write hook files into `C:\Users\Muraghi\.git\hooks\pre-commit`, failing with a `DirectoryNotFoundException` because that directory does not exist or lacks the hooks subdirectory.

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Use `Join-Path (Get-Location)` and verify/create `hooks` directory**
   - **Details**: Resolve hook paths relative to `Get-Location`. Ensure the `.git/hooks` folder is created if it does not already exist before writing files.
   - **Complexity**: Low.
   - **Downstream impact**: Robust path resolution that correctly points to the active workspace repository rather than the process-level home directory.
2. **Option B: Adjust global process directory**
   - **Details**: Update process current directory (`[System.IO.Directory]::SetCurrentDirectory`) to match `(Get-Location).Path`.
   - **Complexity**: Low.
   - **Downstream impact**: Can introduce unintended process-wide side effects and doesn't explicitly document the path target of the hooks writing command.

### Recommendation
Option A is recommended as it keeps path resolution explicit and safe without impacting other threads or commands in the host process environment.

## Tasks
- [x] Task 1: Update hooks path resolution in `bootstrap.ps1` to use `Join-Path (Get-Location)` and ensure hooks directory exists.
- [x] Task 2: Verify the bootstrap script runs successfully without path errors.
- [x] Task 3: Ensure all tests pass.

## Acceptance Criteria
- [x] Git hooks are installed in the correct `.git/hooks` directory of the target project workspace.
- [x] No path-related WriteAllText exceptions are thrown during installation.
- [x] Local validation via `./helper.ps1 validate` passes.
