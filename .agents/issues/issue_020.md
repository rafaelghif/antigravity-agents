---
id: issue-020
title: "Implement Git Profile Manager command in V2 CLI"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3 (standard library only)
- **Architecture**: Modular CLI command under `.agents/scripts/cli/commands/profile.py`, registered in `helper.py`.
- **Key Modules**:
  - [helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py): Register `profile` command.
  - [profile.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/profile.py): Implement the new subcommands (`list`, `switch`, `add`).

## 2. Pre-Implementation Impact Analysis
### Option A: Pure Python CLI Command (Recommended)
- **Complexity**: Low. Parses JSON using `json` module, runs `subprocess` for `git config`.
- **Maintainability**: High. Leverages current helper command loading framework.
- **UI/UX**: Colored, formatted list similar to `git branch`. Instantly updates local Git config on switch.

### Option B: Bash/Shell-based subcommand in helper.sh
- **Complexity**: High. Requires shell script parsing of arguments and JSON parsing (requiring `jq` or Python helpers).
- **Maintainability**: Low. Replicating bash scripts in Windows PowerShell (`helper.ps1`) doubles maintenance footprint.

### Recommendation
Option A is selected for platform portability, code reuse, and compliance with the existing CLI command pattern.

## 3. Implementation Subtasks
- [x] Initialize `git_profiles.json` if not present (copied from `git_profiles.example`)
- [x] Implement `list` subcommand with active indicators (formatted like `git branch`)
- [x] Implement `switch <name>` subcommand to update JSON and apply local Git configurations
- [x] Implement `add <name> <email> [signing_key] [--switch|-s]` subcommand with validation
- [x] Register `profile` command in `helper.py`
- [x] Implement unit tests in `.agents/tests/test_profile.py`
- [x] Validate implementation passes local validations

## 4. Acceptance Criteria
- [x] `helper.py profile list` displays all profiles with a green marker for the active one.
- [x] `helper.py profile switch <name>` updates the active status in `git_profiles.json` and configures local git values (verified via `git config`).
- [x] `helper.py profile add <name> <email> --switch` adds a valid new profile and activates it immediately.
- [x] All unit tests in `.agents/tests/` pass.
- [x] The local validation script `.agents/scripts/validate.py` passes successfully.
