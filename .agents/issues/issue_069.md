---
id: issue-069
title: "Fix Python syntax error in Windows bootstrap script"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
During installation/bootstrapping on Windows, the PowerShell script `bootstrap.ps1` executes inline Python code via `python -c` using single quotes and multi-line strings. PowerShell/Windows command-line parsing does not handle single-quoted multi-line strings correctly when invoking external executables, causing the Python compiler to fail with a SyntaxError (`SyntaxError: invalid syntax` at `if -`).

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Use double-quotes and single-line Python execution**
   - **Details**: Convert the inline Python script into a single-line command enclosed in double quotes, using single quotes for Python string literals.
   - **Complexity**: Low. Very clean and direct.
   - **Downstream impact**: Highly compatible, doesn't require redirection or temporary files.
2. **Option B: Use PowerShell Here-Strings and Stdin piping**
   - **Details**: Store the multi-line Python code in a PowerShell here-string (`@' ... '@`) and pipe it to the python executable (`$PythonScript | python`).
   - **Complexity**: Moderate.
   - **Downstream impact**: Might suffer from encoding/BOM issues in older Windows PowerShell versions (UTF-16 vs UTF-8 piping) when stdin is redirected to external executables.

### Recommendation
Option A is recommended because it is simple, highly portable across PowerShell versions, avoids stdin encoding redirection issues, and resolves the argument parsing bug directly.

## Tasks
- [x] Task 1: Update version synchronization logic in `bootstrap.ps1` to use double-quoted single-line Python command (Option A).
- [x] Task 2: Validate the bootstrap.ps1 script manually to ensure no syntax errors occur.
- [x] Task 3: Verify the workspace is fully compliant by running `.\helper.ps1 validate`.

## Acceptance Criteria
- [x] Windows bootstrapping (`bootstrap.ps1`) completes without Python SyntaxError.
- [x] Version synchronization works and updates/preserves `AGENTS.md` version.
- [x] `./helper.ps1 validate` succeeds.
