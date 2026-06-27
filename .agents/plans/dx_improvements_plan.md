# Implementation Plan: Developer Experience (DX) Improvements

This plan outlines the design and implementation of four core developer experience features to improve usability, setup diagnostics, self-upgrades, global accessibility, and completion.

---

## 1. Feature Specifications

### Milestone 1: Environment Diagnostics CLI (`doctor`)
Implement a `doctor` subcommand in our CLI helper to verify the host environment health.
- **Diagnostics Checks**:
  1. Python 3 environment check.
  2. Git CLI presence & local work tree verification.
  3. Git identity registration (User email & name configurations).
  4. Active workspace git profiles config availability and GPG/SSH key path checks.
  5. Network ping connectivity check to remote repo.
- **Self-Healing fixes**: Provide automated fixes for missing profiles configuration files or unconfigured local options.

### Milestone 2: Core Self-Upgrader (`upgrade`)
Implement a self-updater subcommand to pull the latest versions of code scripts and core components without losing local settings.
- **Execution Flow**:
  1. Fetch latest release/master content from target Git remote repository.
  2. Overwrite files in `.agents/scripts/`, `.agents/templates/`, and root scripts (`helper.sh`, `helper.ps1`).
  3. **Strict Preservation**: Ensure local configurations (`git_profiles.json`, `locks.json`, local project `board.md`, custom files under `.agents/skills/`) are preserved and never overwritten.

### Milestone 3: Global CLI Launcher Alias (`install-global`)
Allow running CLI helpers globally from any directory without relative directory prefixes.
- **Strategy**:
  - Implement a command to install a launcher symlink or script (e.g. `aac` or `agy`) to the user PATH (`~/.local/bin/aac` for Linux/macOS, or environment PATH on Windows).
  - The launcher dynamically resolves the current Git root repository directory (using `git rev-parse --show-toplevel`) and passes all parameters to the local wrapper `./helper.sh` or `./helper.ps1`.

### Milestone 4: Shell Autocompletion (`completion`)
Introduce shell tab-completion scripts to speed up command line invocation.
- **Strategy**:
  - Implement `completion bash` and `completion zsh` commands.
  - Dynamically output completion definitions matching helper commands (`lock`, `validate`, `profile`, `skill`, `issue`, `changelog`) and subcommands.

---

## 2. File Modifiers Plan

- **Modify**:
  - `.agents/scripts/cli/helper.py`: Add subcommands `doctor`, `upgrade`, `completion`, and registry entries.
- **Create**:
  - `.agents/scripts/cli/commands/doctor.py`: Implement environmental diagnosis and troubleshooting.
  - `.agents/scripts/cli/commands/upgrade.py`: Implement remote updates downloading and code replacement.
- **Add Tests**:
  - `.agents/tests/test_doctor.py`: Test environment audits and recovery pathways.
  - `.agents/tests/test_upgrade.py`: Test update downloads and overwrite guards.

---

## 3. Pre-Implementation Impact Analysis

- **Option A: Centralized command modules (Option Selected)**:
  All four utilities are implemented as independent Python subcommands under `.agents/scripts/cli/commands/` and wrapped by `helper.py`. This ensures portability, consistent logging, and full cross-platform compatibility on both Windows and Linux.
- **Option B: Bash/PowerShell specific wrappers**:
  Implement logic in shell/PowerShell wrapper scripts. This is rejected due to double-maintenance overhead and syntax divergence between Bash and PowerShell.
