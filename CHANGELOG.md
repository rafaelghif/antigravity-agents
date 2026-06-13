# Agent Core Changelog

This document tracks all version updates, script refinements, and protocol changes made to the Antigravity Agent Core workspace setup.

## [1.3.1] - 2026-06-13
### Fixed
- Fixed infinite recursion loop in Git hooks installation by adding the `# Antigravity Agent Git Hook` marker to all hook templates and checking it in `install_git_hook_safe`.
- Fixed invalid `local` variable declarations in the global shell scope of `bootstrap.sh`.

### Changed
- Improved linter and test suite command extraction from `project_rules.md` to be format-agnostic, handling backticks, quotes, and raw text formats safely in both `helper.sh` and the `pre-commit` hook.
- Enhanced `bootstrap.ps1` to natively support PowerShell switch `-Force` (`-f`) and `-Version` (`-v`) parameter sets for clean arg forwarding.

---

## [1.3.0] - 2026-06-13
### Added
- Added `-f`/`--force` argument parsing in `bootstrap.sh` and `recon.sh` to control template overwriting.
- Created `install_git_hook_safe` to safely backup pre-existing custom Git hooks (`.backup` suffix) and chain them automatically, preventing developer data-loss.
- Added colorized logs (`log_info`, `log_success`, `log_warning`, `log_error`) for bootstrapper user feedback.
- Added template development repository detection to prevent the root bootstrapper from deleting itself during local development testing.
- Added argument forwarding support in `bootstrap.ps1` for Windows users.

### Changed
- Converted all embedded file, script, and hook generations in `bootstrap.sh` to use `write_template_safe` for full idempotency.
- Refined `recon.sh` database schema generation to avoid string append (`>>`) side-effects.
- Synchronized `AGENTS.md` and `helper.sh` templates inside `bootstrap.sh` with the latest strict multi-agent coordination rules and tools.

---

## [1.2.0] - 2026-06-13
### Added
- Added `pre-commit` Git hook to automate workspace validation checks, linter checks, and test runner suites on standard git commits.
- Refined `post-commit` Git hook to automatically release all active workspace locks upon successful commits, eliminating manual command invocations.
- Added `.antigravityignore` in the project root to exclude dependency, build, OS, binary, and log folders to optimize agent token usage.
- Created `CHANGELOG.md` (this file) at the root to record historical updates of agent rules and scripts.

### Changed
- Updated root `bootstrap.sh` and local backup templates to write Check 5, Check 6, and Check 7 in the validation script.
- Updated `helper.sh` (`cmd_init` and `cmd_doctor`) to copy and verify both hooks.
- Refined `helper.sh archive` command to automatically archive dynamic task workflows (`task_*.md`) and PR guides (`pr_review_*.md`) from `.agents/workflows/` to branch-specific subdirectories under `.agents/archive/`.
- Made bootstrapping rules in `AGENTS.md` and `project_rules.md` stricter: sequence is absolute, and no edits or command executions are allowed before reading the core files.
- Documented `/grill-me` outcomes of the teamwork design alignment in `.agents/workflows/task_teamwork_rules.md`.

---

## [1.1.0] - 2026-06-13
### Added
- Added Git tracking configuration in `.gitignore` to track `AGENTS.md` and all files under `.agents/` (except transient lock files under `.agents/locks/`).
- Added strict Git Upstream Synchronization Check in `validate.sh` to check if HEAD is behind `origin`.
- Added Schema Index Registration Compliance check in `validate.sh` to verify all domain schemas are indexed.
- Set rules requiring all design alignments and `/grill-me` outcomes to be saved as execution plans under `.agents/workflows/task_<task_name>.md`.
- Added Conventional Commit verification support in `helper.sh commit`.

---

## [1.0.0] - 2026-06-13
### Added
- Initial setup of the Antigravity Agent Core.
- Core memory management in `memory.md`.
- Module lock validation, credentials scanning, and domain-purity env scanning in `validate.sh`.
- Tech stack auto-detection in `recon.sh`.
