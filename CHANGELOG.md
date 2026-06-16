# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-06-16

### Added
- Interactive onboarding tutorial subcommand `guide` (`guide.py`).
- Workspace cleanup subcommand `clean` (`clean.py`) to purge locks, archives, reset token budget, reset API key templates, and reset `memory.md`.
- Interactive CLI dashboard menu subcommand `menu` (`menu.py`) providing a categorized text user interface (TUI) to easily execute daily development, diagnostics, and configurations without command-line arguments.
- Comprehensive unit tests in `tests/test_clean_command.py` and `tests/test_menu_command.py` verifying clean logic, interactive prompts, and menu routing.
- Automatic recursive CLI Python scripts packaging in `compile_bootstrap.py` to auto-discover and package CLI files into `bootstrap.sh`.
- Secure Git push subcommand `push` (`push.py`) implementing workspace validation checks, profile email matching, and SSH key rotation.
- Comprehensive unit tests in `tests/test_push_command.py` verifying flags, dry-runs, and SSH environment setup.
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
- Automatic token budget reset feature based on configurable intervals (`hourly`, `daily`, `weekly`, `monthly` or custom seconds) in `token_budget.json`.
- Added new unit test in `tests/test_rotation.py` to verify budget reset on elapsed interval duration.
- Specialized `docs-sync` agent skill to parse Python docstrings using Abstract Syntax Trees (AST) and sync them in-place to target Markdown files between placeholders.
- Comprehensive unit tests in `tests/test_skill_docs_sync.py` covering AST-based parsing, markdown formatting, and placeholder sync.
- Local Issue Tracker subcommand `issue` (`issue.py`) storing issues under `.agents/issues/` and integrating with `helper.sh commit` to auto-close and stage issues via `closes #XX` / `fixes #XX` / `resolves #XX` patterns.
- Comprehensive unit tests in `tests/test_issue_command.py` verifying issue listing, creation, viewing, closing, and git auto-close integrations.
- Expanded `issue` command with branch automation subcommands: `checkout <id>` (auto-creates and switches to issue branches and updates task target in `memory.md`) and `merge <id>` (automatically validates workspace, closes issue, commits branch, merges into base branch, and cleans up local branches).
- Extended `tests/test_issue_command.py` with unit tests for checkout and merge commands, verifying branch creation, memory updates, and mock merge runs.
- Strict Issue-Driven Validation check in `validate.sh` (Check 16) enforcing frontmatter schema format and status compliance for local workspace issues.
- Added rules guidelines for Strict Issue Alignment in `AGENTS.md` and `.agents/rules/project_rules.md` requiring agents to map active development tasks 1-to-1 with local issues.

### Changed
- Registered `push` and `guide` subcommands in CLI helper `helper.py` and documented them in `docs/cli_guide.md`.
- Updated `README.md`, `docs/cli_guide.md`, `docs/agent_workflow.md`, and `docs/setup_guide.md` to reference the onboarding guide and replace raw Git commit commands with secure helper commits.
- Updated CLI utils `utils.py` to automatically trigger token budget reset checks on load.
- Updated `validate.sh` Check 9 to run Python budget reset checks before validating with `jq`.
- Refactored `api-rotator` skill script `main.py` to import CLI `utils` and load the budget through the centralized budget tracker.
- Centralized and standardized all modular documentation files under root `docs/` directory, removing the redundant `.agents/docs/` folder.
- Updated root `README.md` documentation index to link to the new standardized `docs/` paths and included the `api_rotation.md` guide.
- Consolidated all migration documentation into a single, unified `docs/migration_guide.md` file, deleting the redundant `MIGRATION.md` file and updating all CLI command version descriptions to version V1.9.0.
- Refined the default `memory.md` template written by `bootstrap.sh` to be generic, professional, and free of hardcoded project history.
- Added automatic Git branch/commit synchronization (`helper.sh sync-git`) at the end of the installation process in `bootstrap.sh` for plug-and-play workspace alignment.
- Improved error handling in CLI wrappers `helper.sh` and `helper.ps1` to check for Python 3 availability.
- Documented system prerequisites (Git, Python 3, Git Bash) in `README.md`.
- Exempted unit test files and directories from raw environment variable scan warnings, allowing developers to mock configuration values in test suites.
- Optimized validation performance by adding standard virtual envs, build targets, and vendor directories (`venv`, `env`, `target`, `vendor`, `out`) to search exclusions, preventing token budget bloat and massive scan slowdowns.

### Fixed
- Fixed empty Git config email matching bug in secure push command.
- Made Git profiles properties parser in `commit` command robust to optional whitespace surrounding the `=` operator.
- Fixed a logical precedence bug with `-o` in `find` queries inside `validate.sh` that was causing the script to search inside excluded directories like `node_modules` and `.agents`.
- Implemented Python environment access scan (`os.environ`/`os.getenv`) in `validate.sh` to enforce architectural layer boundaries on Python projects.
- Fixed script execution compatibility on Windows by executing `.sh` files with `sh` prefix.
- Resolved Python stub execution crash on Windows in `helper.sh` and `validate.sh` by using the `--version` option to verify executable viability.
- Fixed shebang and OS-specific path issues in unit tests (`docs-sync`, `pr-scaffolder`, `rotation`).
- Fixed missing `CYAN` color initialization and skill directory creation bugs in `bootstrap.sh`.
- Compiled missing skill template files for `adr-wizard`, `docs-sync`, and `pr-scaffolder` into `bootstrap.sh` by updating `compile_bootstrap.py`.
- Fixed docstring backslash regex backreference injection bug in `docs-sync` main script using lambda replacement.

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
