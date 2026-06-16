# Workflow Plan: PowerShell API Profile Rotation & Active Keys Support

This document defines the implementation details and plan for adding native PowerShell API profile rotation, active keys auto-loading, and budget check integrations in the Windows environment.

---

## 1. Architectural Decisions

- **Native PowerShell wrapper (`api-rotate-wrapper.ps1`)**:
  - Located at `.agents/scripts/api-rotate-wrapper.ps1`.
  - Parses `.agents/api_keys` to detect configured profiles and count max retries.
  - Executes wrapped commands and catches rate-limiting exit codes (`429`, `129`, `3`).
  - Calls `helper.ps1 api-profile rotate` to rotate keys and re-imports the updated key file.
- **`helper.ps1` updates**:
  - Detect if `helper.ps1` is dot-sourced. If so, automatically dot-source `.agents/active_api_keys.ps1` after running `api-profile` commands to update environment variables in the caller's session.
  - If NOT dot-sourced, print a friendly reminder instructing the user to run `. .agents/active_api_keys.ps1` to load keys.
- **Compiler Synchronization**:
  - Update `scratch/compile_bootstrap.py` to track `.agents/scripts/api-rotate-wrapper.ps1` and inject its template into `bootstrap.sh`.

---

## 2. Implementation Checklist

- [x] Create `.agents/scripts/api-rotate-wrapper.ps1` with robust rate-limit intercept and retry.
- [x] Refine `.agents/scripts/helper.ps1` to support session key loading and dot-source checks.
- [x] Update `scratch/compile_bootstrap.py` to register the new PowerShell wrapper and auto-insert it if not present.
- [x] Run `python3 scratch/compile_bootstrap.py` to compile templates.
- [x] Verify validation checks pass and commit the changes.
- [x] Clean and release any locks.
