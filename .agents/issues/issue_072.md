---
id: issue-072
title: "Implement AAC V2 Core Enhancements (Points 1-5)"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Implement the five core enhancements outlined in the workspace design plan:
1. **SSH Key Rotation per Profile**: Automatically configure Git's local `core.sshCommand` to use profile-specific keys.
2. **CI/CD Actions Template**: Automatically scaffold GitHub Actions pipeline configurations.
3. **Structured Observability Logs**: Write JSON log audits for CLI commands to `.agents/logs/cli.log`.
4. **Skill CLI Manager**: Create a CLI subcommand to list/install/uninstall skills.
5. **Integration Parity Testing**: Add integration tests for shell and PowerShell wrappers.

## Pre-Implementation Impact Analysis
### Explore Options
1. **Option A: Deploy features as separate wrapper scripts**
   - **Details**: Implement independent scripts for logging, skill installation, and SSH management.
   - **Complexity**: High. Leads to fragmented workflow wrappers and duplicate path resolving code.
2. **Option B: Incorporate all features directly into the helper CLI structure**
   - **Details**: Integrate logging into `helper.py`, SSH rotation into `profile.py`, and create a modular `skill.py` CLI subcommand.
   - **Complexity**: Low. Highly maintainable, clean separation of concerns, and full reuse of CLI argument parsing.

### Recommendation
Option B is selected to ensure all CLI functionality is centralized under `helper.py` and wrapped cleanly by `helper.sh`/`helper.ps1` wrappers.

## Tasks
- [x] Task 1: Update profile rotation to configure Git's local `core.sshCommand` and validate key presence.
- [x] Task 2: Implement CI/CD workflow template and bootstrap scaffolding hook.
- [x] Task 3: Integrate structured JSON logger in helper CLI execution loop.
- [x] Task 4: Implement skill CLI manager command.
- [x] Task 5: Implement wrapper integration tests in test suite.
- [x] Task 6: Verify all tests and validation audits pass.

## Acceptance Criteria
- [x] Profile switch command sets local Git `core.sshCommand` to path-specific keys.
- [x] Bootstrapping a project generates `.github/workflows/verify.yml` automatically.
- [x] Running helper CLI commands appends structured JSON logs to `.agents/logs/cli.log`.
- [x] Skill manager command installs, uninstalls, and lists skills.
- [x] Wrapper integration tests pass successfully.
