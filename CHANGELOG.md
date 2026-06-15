# Agent Core Changelog

This document tracks all version updates, script refinements, and protocol changes made to the Antigravity Agent Core workspace setup.

## [1.7.1] - 2026-06-16
### Added
- Added `git-profile` command in `helper.sh` (and template inside `bootstrap.sh`) to support switching Git configurations locally for multiple accounts, including reading profile keys from `.agents/git_profiles` or `~/.git_profiles`.
- Integrated `.agents/git_profiles` in default `.gitignore` configurations to prevent accidental commits of local credentials.

### Fixed
- Fixed a potential installation hang issue in `validate.sh` / `bootstrap.sh` by introducing a pure-Bash watchdog timer for `git fetch origin`, limiting wait time to 5 seconds without relying on external `timeout` or `gtimeout` commands.
- Restricted `git fetch origin` in validation checks to only run if a remote named `origin` is actually configured in the Git repository.

## [1.7.0] - 2026-06-14
### Added
- Added Windows PowerShell compatibility via `.agents/scripts/helper.ps1` command wrapper, allowing seamless script execution for developers working natively on Windows.
- Added automated GitHub Actions CI workspace validation via `.github/workflows/antigravity.yml` workflow template, running strict credential scans, schema compliance, and system checks automatically on push and pull requests.
- Integrated generation of `helper.ps1` and `antigravity.yml` into the workspace installer (`bootstrap.sh` / `bootstrap.ps1`).

## [1.6.0] - 2026-06-13
### Added
- Added **Workspace Rules Registry** feature to scaffold, audit, and manage dynamic coding rules under `.agents/rules/`.
- Implemented **Legacy rules migration** from the old `.agent/rules/` path to the new `.agents/rules/` path automatically during bootstrap and workspace initialization.
- Added `./.agents/scripts/helper.sh create-rule <name> <activation> [param]` subcommand to scaffold rule markdown files supporting multiple activation modes (manual, always-on, glob, and model-decision).
- Added `./.agents/scripts/helper.sh list-rules` subcommand to list all registered rules and audit them for compliance (naming, valid frontmatter, activation configuration parameters, and absence of placeholders).

## [1.5.0] - 2026-06-13
### Added
- Added **Automated Skill Registry** feature to scaffold, audit, and manage specialized agent skills.
- Added `./.agents/scripts/helper.sh create-skill <name> [description]` to scaffold a new specialized skill directory containing `SKILL.md` and a structured, executable Python template at `scripts/main.py`.
- Added `./.agents/scripts/helper.sh list-skills` to dynamically audit and verify Keep-a-Skill compliance for all registered skills.
- Implemented **Agent-Initiated Dynamic Skill Self-Creation** protocol allowing the agent to autonomously generate, audit, test, and commit new specialized capabilities upon detecting functional gaps.
- Resolved and cleaned up backslash escaping bugs inside the helper script templates in `bootstrap.sh` to ensure clean workspace upgrades and syntax-error-free bootstrapping.

## [1.4.1] - 2026-06-13
### Added
- Added automatic version bump utility via `helper.sh release <major|minor|patch>` to automatically increment versions and comparison links in `CHANGELOG.md`.

## [1.4.0] - 2026-06-13
### Added
- Added Token Budget Guard (Check 9) in `validate.sh` to monitor token usage and enforce auto-saving progress when limits are reached.
- Added `helper.sh log-usage <count>` command to log token counts dynamically into `.agents/token_budget.json`.
- Hardened agent security by adding environment secrets (`.env*`), cryptographic keys (`*.pem`, `*.key`), and credential configurations to `.antigravityignore` to programmatically block the agent from crawling or indexing sensitive configurations.
- Added Section 7 (Autonomous Operational Scripts & Commands) to project rules blueprint, instructing agents to autonomously invoke helper commands (`lock`, `unlock`, `validate`, `doctor`, `archive`, `sync-api`) without manual user intervention.
- Added automated API Contract Synchronization feature via `helper.sh sync-api`, extracting `openapi.json` from backend stacks and writing zero-dependency typed TypeScript clients in the frontend.
- Created zero-dependency Node.js parser at `.agents/scripts/generate-client.js` to convert `openapi.json` schemas into fully-typed fetch API client wrapper classes.
- Added Next.js, Go Gin, and FastAPI boilerplates to the workspace scaffolding wizard (`helper.sh init`).
- Added a **Monorepo** template option in scaffolding (`helper.sh init`) which sets up a Turborepo + pnpm layout containing Next.js frontend (`apps/web`), Go Gin backend (`apps/api`), and shared workspace packages (`packages/shared`).
- Added a **Custom Multi-Project / Separate Apps** scaffolding option (`helper.sh init`) allowing users to choose and combine different backend stacks (NestJS, FastAPI, Go Gin) and frontend stacks (Next.js, React SPA, Laravel Blade/HTML) with decoupled layouts.
- Added native directory scaffolding for multiple architecture layouts: **Hexagonal Architecture** (domain, ports, adapters), **Clean Architecture** (entities, usecases, controllers), and **Atomic Design** (atoms, molecules, organisms, templates).
- Added **Docker and Docker Compose scaffolding** to the initialization wizard (`helper.sh init`), automatically writing multi-stage `Dockerfile` configurations and network-bridged `docker-compose.yml` deployments.
- Integrated **database healthcheck verification** and startup sequence ordering (`depends_on` with `service_healthy` conditions) for PostgreSQL, MySQL, MongoDB, and Redis.
- Resolved potential host port collisions by dynamically offsetting frontend ports (e.g., mapping host port `3001` to container port `3000`) if the backend binds to port `3000`.
- Added automatic workspace migration utility (`helper.sh migrate`) that safely backs up user settings, updates workspace structures, handles hook alignment, and updates active memory schema configuration.
- Created standalone `MIGRATION.md` detailing automated and manual workspace upgrades.
- Enhanced `recon.sh` to natively detect monorepos (Turborepo, Yarn/pnpm workspaces, Go workspaces) and configure sub-project mappings inside `.agents/subprojects.sh` and `project_rules.md`.
- Added a fallback scanner in `recon.sh` to auto-discover and map nested projects under `apps/`, `packages/`, or `services/` even if a root workspace configuration file (like `turbo.json` or `pnpm-workspace.yaml`) is not present.
- Added monorepo-aware linter, builder, and testing execution inside `helper.sh` (`helper.sh build/lint/test`) which parse subprojects and dynamically execute validations only on directories containing staged modifications.
- Modified lock/unlock command to sanitize slash paths in module names (e.g., `apps/backend` locks as `apps_backend.lock`), avoiding path conflicts.

### Changed
- Updated bootstrapper initialization to run autonomous stack discovery with `--force` internally, writing clean, optimized lint, build, and test runner configurations to `project_rules.md`.
- Modified bootstrapper doctor step to run non-destructively without aborting on active local development warnings.

---

## [1.3.2] - 2026-06-13
### Added
- Added **Handover Protocol (Relayed Context)** support to allow seamless turn/account continuation.
- Added Section 3 `Relayed Context & Handover Notes` in the `.agents/memory.md` template.
- Documented Handover rules in both `AGENTS.md` and `.agents/project_rules.md` templates.

---

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

[1.7.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/rafaelghif/antigravity-agents/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/rafaelghif/antigravity-agents/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/rafaelghif/antigravity-agents/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/rafaelghif/antigravity-agents/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rafaelghif/antigravity-agents/releases/tag/v1.0.0

