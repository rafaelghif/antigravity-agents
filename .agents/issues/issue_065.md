---
id: issue-065
title: "Fix Windows installation and bootstrap completeness"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The installation on Windows is incomplete because the Windows installation command runs `bootstrap.ps1` directly, which only performs bootstrapping (directory layout, git hooks, and auto-reconnaissance) but does not download the repository ZIP, extract, and install the `.agents` folder, skills, CLI scripts, helper commands, and `AGENTS.md` like `install.sh` does on Ubuntu/Linux.

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Integrate download and extraction directly into `bootstrap.ps1`**
   - **Complexity**: Moderate. `bootstrap.ps1` becomes a larger script doing both HTTP downloads/extraction and bootstrapping.
   - **Parity**: Breaks parity with Linux since Linux uses `install.sh` for download/install and `bootstrap.sh` for post-copy bootstrap.
   - **Downstream impact**: Upgrades and clean installs would run the same script. If run locally, it needs complex conditions to avoid downloading if files are already local.
2. **Option B: Create `install.ps1` to mirror `install.sh`, and keep `bootstrap.ps1` to mirror `bootstrap.sh`**
   - **Complexity**: Clean. We create a dedicated installer `install.ps1` that handles download, directory backup, file copying, and invokes `bootstrap.ps1` for configuration. We then update the Windows command in `README.md` to download and run `install.ps1` instead of `bootstrap.ps1`.
   - **Parity**: Perfect parity with Linux/macOS architecture.
   - **Downstream impact**: Much easier to maintain, highly clean separation of concerns.

### Recommendation
Option B is highly recommended. It maintains consistency with our Linux/macOS script architecture (`install.sh`/`bootstrap.sh` vs `install.ps1`/`bootstrap.ps1`), prevents script bloat, and provides the cleanest, most maintainable implementation.

## Tasks
- [x] Task 1: Create `install.ps1` implementing the full Windows installer workflow (Git/Python check, target folder setup, backup, GitHub repository ZIP download/extraction, file copying, and running `bootstrap.ps1`).
- [x] Task 2: Update `bootstrap.ps1` to make sure it handles git hooks and directory setups correctly and robustly.
- [x] Task 3: Update `README.md` installation instructions for Windows to use `install.ps1` instead of `bootstrap.ps1`.
- [x] Task 4: Run validation audits (`./helper.sh validate`) and verify correctness.

## Acceptance Criteria
- [x] Windows installation command successfully downloads and installs all files including `.agents/skills`, `.agents/scripts`, `helper.ps1`, `helper.sh`, and `AGENTS.md`.
- [x] `install.ps1` supports local development directory installations when `ANTIGRAVITY_LOCAL_DEV` environment variable is set.
- [x] `install.ps1` supports backup of existing `.agents` folders and `AGENTS.md` files during upgrades.
- [x] Validation suite passes successfully.
- [x] Version and changelog are updated via conventions.
