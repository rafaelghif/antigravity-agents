# Agent Core Changelog

This document tracks all version updates, script refinements, and protocol changes made to the Antigravity Agent Core workspace setup.

---

## [1.2.0] - 2026-06-13
### Added
- Added `pre-commit` Git hook to automate workspace validation checks, linter checks, and test runner suites on standard git commits.
- Refined `post-commit` Git hook to automatically release all active workspace locks upon successful commits, eliminating manual command invocations.
- Added `.antigravityignore` in the project root to exclude dependency, build, OS, binary, and log folders to optimize agent token usage.
- Created `.agents/CHANGELOG.md` (this file) to record historical updates of agent rules and scripts.

### Changed
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
