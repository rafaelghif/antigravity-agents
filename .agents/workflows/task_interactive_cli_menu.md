# Task Workflow: Implement Interactive CLI Menu Dashboard

This task adds an interactive, user-friendly console dashboard menu (TUI) to the Antigravity CLI. It launches automatically when the helper is run with no arguments in an interactive terminal, or explicitly via the `menu` command.

## 1. Architectural Decisions & Mappings
- **Command Entrypoint**: `./.agents/scripts/helper.sh` (when interactive with no args) or `./.agents/scripts/helper.sh menu`
- **Implementation File**: [menu.py](file://../../.agents/scripts/cli/commands/menu.py)
- **Features & Logic**:
  - **Auto-Launch TTY Gate**: If no arguments are provided to `helper.py`, check if `sys.stdin.isatty()` is True. If so, launch the menu; otherwise, print standard help and exit with code 1.
  - **Categorized Dashboard**: Present option sections for Daily Development (lock, unlock, commit, push), Diagnostics (doctor, validate), Profiles (git-profile, api-profile, adr-wizard), and Utilities (guide, clean, archive, recon).
  - **Auto-Scanned Unlock**: Instead of typing module names, scan `.agents/locks/` and display a numbered list of active locks for quick unlocking.
  - **Interactive Profile Switcher**: Scan `git_profiles` and `api_keys` to allow switching profiles by number selection.
  - **Clean Safety Prompt**: Prompt with a clear warning and `(y/N)` confirmation before running the `clean` subcommand.

---

## 2. Implementation Checklist

- [x] **Create `menu.py` Command Module**
  - Implement the dashboard selection loop, inputs, lists scanning, and command execution delegation in [menu.py](file://../../.agents/scripts/cli/commands/menu.py).
- [x] **Register `menu` Command and Auto-Launch Gate**
  - Import `menu` in [helper.py](file://../../.agents/scripts/cli/helper.py).
  - Update `main()` in [helper.py](file://../../.agents/scripts/cli/helper.py) to execute the menu command when no arguments are passed and stdin is a TTY.
- [x] **Verify and Validate**
  - Run `./.agents/scripts/helper.sh` and test all options.
  - Verify non-interactive execution (e.g. `helper.sh --help` or pipe input) prints standard help and does not hang.
- [x] **Document Changes**
  - Update `docs/cli_guide.md` and `CHANGELOG.md` under the current version.
  - Re-run `scratch/compile_bootstrap.py` to compile new scripts into `bootstrap.sh`.
- [x] **Release Locks & Commit**
  - Run `./.agents/scripts/helper.sh commit feat cli "add interactive console dashboard menu"`
