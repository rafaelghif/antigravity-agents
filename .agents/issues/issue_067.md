---
id: issue-067
title: "Align and synchronize installation and bootstrap scripts across OSs"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Ensure full parity and robustness between Unix/Linux and Windows installation and bootstrap scripts to avoid platform-specific discrepancies. Specifically:
1. Make path-based exclusions in `install.ps1` match both backslashes (`\`) and forward slashes (`/`).
2. Add template copy logic to `bootstrap.sh` to mirror the standalone capabilities of `bootstrap.ps1`.
3. Align the pre-commit hook in `bootstrap.sh` to check for both `python3` and `python` (instead of just `python3`), matching `bootstrap.ps1`.

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Leave the small discrepancies as they are**
   - **Complexity**: Zero immediate work.
   - **Downstream impact**: Leads to hidden failures and divergent behaviors on different platforms (e.g. running `bootstrap` directly on Linux wouldn't set up memory templates, while on Windows it does; Python checks in hooks differ).
2. **Option B: Proactively synchronize all script features and path formats**
   - **Complexity**: Very low. Requires small, targeted alignment edits to `install.ps1` and `bootstrap.sh`.
   - **Downstream impact**: Guarantees identical operational behavior on both platforms, satisfying the user's need for strict environment reliability.

### Recommendation
Option B is the recommended path for robust cross-platform parity.

## Tasks
- [x] Task 1: Update path exclusions in `install.ps1` to be directory-separator agnostic (match both `/` and `\`).
- [x] Task 2: Align `bootstrap.sh` directory scaffolding and template copying with `bootstrap.ps1` (making `bootstrap.sh` capable of copying memory templates).
- [x] Task 3: Align pre-commit hook Python check in `bootstrap.sh` with `bootstrap.ps1`.
- [x] Task 4: Run validation audits to verify correctness.

## Acceptance Criteria
- [x] Path exclusions in `install.ps1` work on Windows with any separator character.
- [x] `bootstrap.sh` and `bootstrap.ps1` exhibit identical behavior for scaffolding, template copying, and hook generation.
- [x] Validation suite passes.
