---
id: issue-062
title: "Fix Windows installation execution policy error"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Windows PowerShell blocks script execution by default due to Execution Policies (`Restricted` or `AllSigned`). The documented Windows bootstrap command in `README.md` fails because it attempts to execute `.\bootstrap.ps1` directly without bypassing this policy.

## Pre-Implementation Impact Analysis

### Option A: Spawn Child PowerShell with Bypass Argument
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1" -OutFile "bootstrap.ps1"; powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
```
* **Pros**: Simple, execution policy bypass is strictly confined to the execution of `bootstrap.ps1`.
* **Cons**: Spawns a child process. If the user is running PowerShell Core (`pwsh.exe`), calling `powershell` will fallback to Windows PowerShell 5.1, which might lead to version mismatches or profile leakage.

### Option B: Set ExecutionPolicy Bypass for Process Scope (Recommended)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1" -OutFile "bootstrap.ps1"; .\bootstrap.ps1
```
* **Pros**: Bypasses the restriction only for the current PowerShell session (process scope). Does not require Admin/elevation. Runs in the exact same PowerShell version (`powershell.exe` or `pwsh.exe`) the user is already using.
* **Cons**: Affects any other scripts run in the current terminal window/tab until it is closed.

### Recommendation
Option B is recommended. It is the industry standard approach for running one-liner installer scripts in PowerShell (used by tools like Scoop, Chocolatey, etc.). It respects the user's active PowerShell shell version and avoids child process compatibility issues.

## Tasks
- [x] Update Windows bootstrap installation commands in `README.md` to include Process-level ExecutionPolicy Bypass. <!-- id: subtask-readme-update -->

## Acceptance Criteria
- [x] Windows installation commands in `README.md` successfully bypass script execution policies.
- [x] Validation suite passes.
