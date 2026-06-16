# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-06-16

### Added
- Shell autocompletion subcommand `autocomplete` (`autocomplete.py`) for Bash and Zsh.
- Automatic unit test scaffolding for newly created skills (`tests/test_skill_<name>.py`).
- Test runner integration in `tests/test_rotation.py` to automatically discover and run all `test_skill_*.py` files.
- GitHub Actions CI/CD verify workflow `.github/workflows/verify.yml` to automate workspace validation and tests.
- Python virtual environment `.venv` auto-detection in `helper.sh` and `helper.ps1`.
- Virtual environment creation flag `-v` / `--venv` / `--create-venv` support in `bootstrap.sh`.
- Compliant Git PR Review Scaffolder skill `pr-scaffolder` (`.agents/skills/pr-scaffolder/`) to generate review guides with symbol tracking, verification logging, and schema diffing.
- Comprehensive unit tests in `tests/test_skill_pr_scaffolder.py` covering language-agnostic symbol parser and report formatter.
- Interactive guided ADR wizard skill `adr-wizard` (`.agents/skills/adr-wizard/`) with helper subcommand delegation supporting both interactive console prompts and non-interactive JSON parameter modes.
- Enhanced ADR validation checks in `validate.sh` enforcing numeric sequence continuity, bidirectional index sync, and content validation.
- Comprehensive unit tests in `tests/test_skill_adr_wizard.py` covering help execution and non-interactive generation.

### Changed
- Centralized and standardized all modular documentation files under root `docs/` directory, removing the redundant `.agents/docs/` folder.
- Updated root `README.md` documentation index to link to the new standardized `docs/` paths and included the `api_rotation.md` guide.
- Improved error handling in CLI wrappers `helper.sh` and `helper.ps1` to check for Python 3 availability.
- Documented system prerequisites (Git, Python 3, Git Bash) in `README.md`.

## [1.8.0] - 2026-06-16

### Added
- Modular Python CLI framework under `.agents/scripts/cli/` to replace the monolithic 4,600+ lines `helper.sh`.
- Subcommand command modules in `.agents/scripts/cli/commands/`:
  - `lock.py`: Handle transient domain/module locks.
  - `validate.py`: Handle strict workspace validation checks.
  - `doctor.py`: Diagnostics and syntax auditing.
  - `migrate.py`: Backup checks, hook updates, and `.gitignore` guard installations.
  - `git_profile.py`: local git user configuration profiles and SSH keys rotation.
  - `api_profile.py`: API credential switching and cooldown management.
  - `log_usage.py`: token budget tracker.
  - `recon.py`: wraps auto-reconnaissance.
  - `skills.py`: CLI actions for listing and creating skills.
  - `rules.py`: CLI actions for listing and creating rules.
  - `init.py`: Scaffolds tech-stack boilerplate configurations dynamically.
  - `sync_git.py`: Syncs active Git branch and commit references.
  - `build.py`: Runs monorepo/single project build validation commands.
  - `lint.py`: Runs linter commands.
  - `test.py`: Runs test suites.
  - `sync_api.py`: Synchronizes API contract endpoints and TypeScript clients.
  - `create_adr.py`: Creates Architectural Decision Records.
  - `release.py`: Auto-bumps semver version in changelogs.
  - `commit.py`: Round-robin git profile and SSH rotation commit runner.
- Added `utils.py` containing unified token usage budgeting, logging, and warning handlers.

### Changed
- Refactored `helper.sh` and `helper.ps1` into thin wrappers forwarding commands directly to `python3 .agents/scripts/cli/helper.py`.
- Optimized prompt cache hit rate and token consumption during daily agent commands.

[1.9.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.7.4...v1.8.0
