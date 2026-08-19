# Changelog

## [4.4.27] - 2026-08-19

### MCP Database Support
- Added official MCP server template configurations in `.agents/mcp_config.json.example` for PostgreSQL, MySQL, and Microsoft SQL Server (MSSQL).
- Supports fully customizable connection ports via environment variables (`DB_PORT_PG`, `DB_PORT_MYSQL`, `DB_PORT_MSSQL`).
- Updated `.env.example` with the necessary payload variables.

## [4.4.26] - 2026-08-19

### Architecture (Bot Mode)
- **Multi-Agent Collaboration Room**: Implemented `scripts/inbox_manager.py` as an asynchronous pub-sub message router for subagents.
- **Debate Limits**: Subagents (`implementer` and `reviewer`) now log their handoffs via the Inbox. If a debate loop exceeds 3 turns, the room automatically freezes and escalates to a human or planner, preventing infinite context/token burn.

## [4.4.25] - 2026-08-19

### Persona Update
- **Chill Gen-Z L9 Engineer**: Refactored the core `<PERSONA>` in `AGENTS.md`. Ripped out the stiff AI corporate language. Injected a natural, casual, and highly aggressive Anti-Yes-Man persona. Expect brutal honesty without the cringe.

## [4.4.24] - 2026-08-19

### Features
- **Smart Upgrade Logic**: Installers (`install.sh`, `install.ps1`) now dynamically detect if they are performing a clean install or an upgrade.
- **Procedural Memory Preservation**: During an upgrade, the installer will no longer blindly overwrite `.agents/brain/rules.md`, strictly preserving the user's localized self-learned rules while still backing up the entire agent core to `.agents-backups/`.

## [4.4.23] - 2026-08-19

### Chores
- **Workspace De-cluttering**: Purged legacy `release_notes_v4.4.x.txt` files and `scratch/` script dumps from version control. Added strict `.gitignore` rules to prevent temporary file leakage in the future.

## [4.4.22] - 2026-08-19

### Architecture
- **AST X-Ray Vision**: Resolved "Blind Refactoring" context limitations. Subagents (`planner`, `reviewer`) are now mandated to execute `semantic_grapher.py` to extract codebase AST maps *before* conducting impact analysis or multi-file refactors. This ensures no interconnected functions are missed while maintaining O(1) context efficiency.

## [4.4.21] - 2026-08-19

### Performance
- **Memory Compaction Engine**: Addressed token bloat by prohibiting subagents from loading the entirety of `rules.md` blindly. Agents are now mandated to use targeted `grep_search` to load context. 
- **Self-Pruning Memory**: Introduced a strict 50-line limit for `rules.md`. Agents must proactively rewrite and prune obsolete architectural lessons to conserve token bandwidth.

## [4.4.20] - 2026-08-19

### Features
- **[SELF_LEARNING]**: Activated the Procedural Memory engine. All subagents are now forced to inject `.agents/brain/rules.md` before execution to establish long-term learning.
- **Anti-Yes-Man Persona**: Agents will now aggressively push back against suboptimal architectures instead of blindly agreeing.
- **Semantic Grapher Tests**: Added full test coverage for the AST parser (`scripts/semantic_grapher.py`) ensuring stability for Python, TS, and Go AST extraction.
- **Subagent Consistency**: Implemented `<ENTERPRISE_STANDARDS>` across all skills and enforced mandatory memory injection across all subagent protocols.

All notable changes to the Antigravity Agent Core (AAC) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.4.19] - 2026-08-19

### Added
- **Semantic Graphing**: Introduced `scripts/semantic_grapher.py` and `semantic-graphing` skill to allow the agent to parse Abstract Syntax Trees (AST) and build a structural map of the workspace instead of using blind grep.

## [4.4.18] - 2026-08-19

### Changed
- **End-to-End Feature Completeness**: Upgraded `[NO_PLACEHOLDERS]` to `[END_TO_END_COMPLETION]` in `AGENTS.md` and added `Feature Completeness` to `code-quality/SKILL.md`. Mandates that agents MUST deliver 100% complete, fully wired features (DB + API + UI) without skipping edge cases or using half-assed mock data.

## [4.4.17] - 2026-08-19

### Added
- **Anti-Hallucination (`[TRUTH_SEEKING]`)**: Mandates the use of `search_web`, documentation reading, or `pro` subagent invocation instead of guessing logic or schemas.
- **Zero Dummy Code (`[NO_PLACEHOLDERS]`)**: Strictly forbids writing `// TODO` placeholders or dummy variables unless explicitly asked.
- **Industrial Security**: Added strict PBAC/ABAC/RBAC rules to `security/SKILL.md` to prevent dummy roles.

### Fixed
- **Skill Injection Gap**: Forced `planner` and `implementer` subagents to execute `view_file` on `SKILL.md` before coding to ensure rules are actually loaded into context.

## [4.4.16] - 2026-08-19

### Added
- **Long-Term Memory (`.agents/brain/rules.md`)**: Bootstrapped a persistent memory file to support the `/learn` slash command and autonomous mistake tracking.
- **Autonomous Execution Constraints**: Added `[AUTONOMOUS_EXECUTION]` and `[SELF_LEARNING]` to `AGENTS.md` to formally enable non-stop `/goal` workflows and mandate memory persistence.

### Changed
- **Repository Identity**: Revamped `README.md` to highlight AAC's true capabilities: Autonomous Goal-Seeking, Self-Learning, Atomic Rollbacks, and Design/UX Mastery.

## [4.4.15] - 2026-08-19

### Added
- **Design Skill (`.agents/skills/design/SKILL.md`)**: Added explicit UI/UX agent instructions to strictly adhere to CLI-first component generation, framework-specific tooling (Tailwind/Shadcn), mobile-first responsiveness, accessibility (a11y), and proper UI states (Loading/Error/Empty).

### Changed
- **CLI-First Paradigm**: Added the `[CLI_FIRST]` constraint in `AGENTS.md` and `implementer.md` to outright ban manual boilerplate creation. Agents are now required to use native CLI generators (e.g., `nest g`, `ionic g`, `npx shadcn-ui add`) for structural generation.

## [4.4.14] - 2026-08-19

### Changed
- **Agent Orchestration**: Enforced strict `[ORCHESTRATE]` constraints in `AGENTS.md` to prevent agent from attempting complex implementations without delegating to `planner` and `implementer`.
- **Agent Context Control**: Mandated `grep_search` and targeted code reads in `AGENTS.md` to prevent context bloat from blindly reading large files.
- **Agent Rollbacks**: Instructed `implementer.md` to automatically `git restore .` and revert the working tree to a clean state if the healing loop fails 3 times.
- **Peer Review Loop**: Added an explicit step in `implementer.md` to invoke the `reviewer` subagent via message before committing.

## [4.4.13] - 2026-08-19

### Changed
- **Agent Behavior**: Updated `AGENTS.md` and `implementer.md` to mandate atomic commits using Git Conventional Commits after successful file modification and verification. This ensures state is cleanly checkpointed and makes rollbacks trivial.

## [4.4.12] - 2026-08-19

### Fixed
- **Verification Loop**: Added `--execute` flag to `scripts/verify.py` and updated hooks and agents to strictly execute tests instead of just detecting them.
- **Hook Feedback**: Fixed `.agents/hooks.json` to properly capture test output and return JSON prompts on failure.
- **Security Automation**: Enhanced `security/SKILL.md` to mandate the use of automated scanning tools like `gitleaks` and `semgrep`.
- **Installer Coupling**: Made `scripts/validate.py` more modular by separating optional templates from required files.
- **Review Schema**: Added strict JSON schema constraints for outputting reviews in `reviewer.md`.

## [4.4.11] - 2026-08-15

### Added
- **Developer Experience**: Added GitHub Issue templates and Pull Request templates to standardise human and AI contributions.
- **Resilience**: Added Python unit tests (`tests/test_verify.py` and `tests/test_validate.py`) and integrated them directly into `.github/workflows/agent-gates.yml` via `pytest` to prevent systemic regressions.

### Fixed
- **Edge Case Elimination**: Hardened `scripts/validate.py` and `scripts/verify.py` to prevent crashes when JSON config blocks are absent or when files cannot be loaded (`KeyError`, `FileNotFoundError`, `OSError`).
- **Contract Strictness**: Fixed an invalid auto-verify wrapper in `hooks.json` and anchored its regex execution string.

## [4.4.9] - 2026-08-15

### Changed
- **Realistic LLM Boundaries**: Audited and corrected instances of over-confident prompting across `.agents/brain/` (`rules.md`, `soul.md`) and `.agents/common/utils.md`. Replaced strict negative constraints ("Never claim...", "Never place...") with positive, realistic execution boundaries to match the stochastic nature of Large Language Models.
- **Honest Documentation**: Revised `README.md` to remove mathematically impossible marketing claims ("zero-hallucination", "ensure") and replaced them with technically accurate descriptions ("hallucination-resistant", "strongly guide") emphasizing the AI's role as a co-pilot rather than an infallible entity.

## [4.4.8] - 2026-08-15

### Added
- **Enterprise-Grade Code Quality Boundaries**: Upgraded the `code-quality` skill to strictly enforce SOLID principles, Cyclomatic Complexity limits, Descriptive Self-Documenting code, and Resilient Error Handling (graceful degradation).
- **Enterprise-Grade Architecture Standards**: Upgraded the `architecture` skill to mandate Scalability (Big-O analysis), Stateless service layers, optimized Database Performance (Index utilization, N+1 query prevention), and absolute Separation of Concerns.

## [4.4.7] - 2026-08-15

### Changed
- **Branding & Presentation**: Completely overhauled `README.md` to feature a modern, eye-catching, and highly readable layout using flat-square badges, center-aligned headers, structured emoji grids, and concise marketing copy. Replaced dense, hard-to-read text blocks with clear architectural bullet points and logical workflow steps without exaggerating capabilities.

## [4.4.6] - 2026-08-15

### Changed
- **Gemini Context Optimization**: Conducted a final round of LLM Prompt Engineering across all `AGENTS.md`, custom agents (`.agents/agents/*.md`), and skills (`.agents/skills/*.md`). Replaced all negative constraints (e.g., "Do not edit", "NEVER guess") with strict explicit positive boundary constraints (e.g., "Restrict your actions exclusively to...", "Constrain your edits to...") to ensure optimal zero-shot parsing by Gemini 1.5 Pro and other high-reasoning LLMs.

## [4.4.5] - 2026-08-15

### Fixed
- **Installer Security Gaps**: Hardened `install.sh` and `install.ps1` to prevent typosquatting (`rafaelghifari` to `rafaelghif`), applied `umask 077` for state directories, added `--` argument boundaries to prevent injection, bound `-LiteralPath` in PowerShell to avoid wildcard hijacking, and implemented rollback mechanisms (`trap`/`catch`) to prevent zombie states upon partial failure.
- **CI/CD Resiliency**: Fixed PEP 668 external environment crash by migrating `semgrep` install to `pipx`. Added file existence guards (`if [ -f "$f" ]`) in `agent-gates.yml` to prevent arbitrary `FileNotFoundError` pipeline crashes.
- **Stack Detection Bug**: Hardened `scripts/verify.py` to gracefully handle `JSONDecodeError`, `AttributeError`, and `TypeError` when scanning malformed or empty `package.json` manifests.
- **MCP Configuration Formatting**: Fixed Gitea server ENV argument to use the native MCP `"env": {}` object instead of shell flags to prevent interpolation loss. Corrected `postToolUse` camelCase syntax and regex matchers in `hooks.json`.
- **Sub-Agent Logic**: Added bounded `max_retries="3"` constraints to the `implementer` agent's verification loop to prevent token-burning infinite loops.
- **Prompt Clarity**: Abstracted operational bloat from `TASK_TEMPLATE.md` to prevent LLM copy-paste corruption.

## [4.4.4] - 2026-08-15
- **Sub-Agent Restructuring**: Upgraded `.agents/agents/*.md` (implementer, planner, reviewer, security-reviewer) to utilize `<CRITICAL_DIRECTIVE>` and `<PROCEDURAL_WORKFLOW>` XML prompting mechanisms, aligning them with the L9 Expert framework.

## [4.4.3] - 2026-08-15

### Changed
- **Skill Restructuring**: Completely overhauled `.agents/skills/*.md` to align with official Antigravity best practices (removed generic computer science theory, added strict Procedural Workflows and Autonomous CI/CD loops).
- **Mandatory Triggers**: Updated `AGENTS.md` with `<MANDATORY_SKILL_TRIGGERS>` and `<CRITICAL_SYSTEM_DIRECTIVES>` XML blocks to enforce deterministic skill activation.

## [4.4.2] - 2026-08-15
- **Auto-verification Hook**: Added `hooks.json` to automatically trigger `scripts/verify.py` after code modification tools (`write_to_file`, `replace_file_content`, `multi_replace_file_content`) are used.
- **MCP Setup Skill**: Added `mcp-setup` skill to easily initialize Copilot and other external MCP tools from the example config.

### Changed
- Clarified that `.agents/config.json` is a custom internal schema for scripts, not an official Antigravity manifest.

## [4.4.1] - 2026-08-15

### Fixed
- Prevented `install.sh` and `install.ps1` from unnecessarily backing up empty directories on fresh installations.

## [4.4.0] - 2026-08-05

### Changed
- **Compact Always-On Policy**: Replaced the oversized procedural `AGENTS.md` with a behavior-first policy under 600 words.
- **Focused Skills**: Replaced six broad, duplicated skills with four task-specific skills for quality, verification, security, and architecture.
- **Discoverable Custom Agents**: Added planner, implementer, reviewer, and security-reviewer agents using the official `.agents/agents/*.md` format.
- **Stack-Aware Verification**: Added `scripts/verify.py` to detect available project commands instead of guessing generic test commands.
- **Instruction Budgets**: CI now validates and rejects oversized always-on, agent, or skill instructions.

## [4.3.5] - 2026-08-05

### Security
- **Scoped Permission Baseline**: Added sandbox-first settings with explicit command, file, URL, and MCP approval boundaries.
- **Recovery Validation**: Added checks for active-plan state, forbidden legacy state, scanner applicability, compatibility metadata, and structured release markers.

### Changed
- **Installer Safety**: Installers validate the staged release before mutation, use one immutable documented ref, back up every managed target, clean temporary state, and preserve user additions.
- **Windows Coverage**: Added a Windows CI job that parses the PowerShell installer.
- **Compatibility Boundary**: Documented `.agents/` as the Antigravity surface and `opencode.json` as optional OpenCode-only configuration.

## [4.3.4] - 2026-08-05

### Security
- **Antigravity Permission Baseline**: Added a sandbox-first settings example using review-oriented artifact handling and workspace-only access.
- **CI Least Privilege**: Restricted GitHub Actions to `contents: read` and added manual workflow dispatch.
- **Mutable MCP Reference Removed**: Replaced the Gitea MCP `latest` image reference with a versioned image tag.

### Changed
- **Official MCP Schema**: Updated workspace MCP examples to use Antigravity's documented `serverUrl` property.
- **Workspace Skill Discovery**: Flattened all six skills to `.agents/skills/<name>.md` with documented YAML frontmatter.
- **Reproducible Installers**: Linux and Windows installers now target a release ref, clean up temporary state, back up overwritten files, preserve local state, and validate the installed workspace.
- **Structural Validation**: Added a dependency-free validator for Antigravity MCP, skills, manifest, version, and mutable dependency contracts.
- **Active Plan Portability**: Tracked the active plan while retaining local-only audit, scratch, incident, and backup state.

## [4.3.3] - 2026-08-05

### Security
- **Hardcoded GitHub PAT Removed**: `opencode.json` now references the token via `{env:GITHUB_PAT}` interpolation instead of an inlined classic PAT. **Action required**: revoke the previously-committed token (`ghp_20E9…`) in GitHub Settings and re-issue before setting `GITHUB_PAT`.
- **Config Leak Surface Reduced**: `opencode.json` added to `.gitignore` so local MCP header config is never tracked.

### Changed
- **Skill Version Range Bumped**: All 6 core domain skills now declare `requires_core: ">=4.3.3"` (was `>=4.3.0`), matching the canonical `core_version`.
- **Semgrep Version Pinned**: `agent-gates.yml` SAST step now pins `semgrep==1.138.0` to eliminate flaky, network-dependent unpinned installs.
- **Stale-Version Sentinel Extended**: Version-consistency check now also rejects `4.3.2`/`V4.3.2` alongside earlier stale versions.

### Added
- **Tier-Aware Hard Gate**: The pre-execution HARD GATE is now tiered — T1 patches (`< 50 lines`, single file, no contract change) follow a fast path and are exempt from the Issue/Plan/PR ceremony, resolving the direct contradiction between `§2/§5` and the Tiered Execution Engine. T2/T3 retain the full Issue → Plan → Branch → PR → Merge workflow.
- **Complete Directory Manifest**: Restored the full manifest in `AGENTS.md §1` (added `common/`, `incidents/`, `config.json`, `mcp_config.json(.example)`, `TASK_TEMPLATE.md`, `brain/env-required.json`, `brain/schemas/`).
- **MIT License**: Added `LICENSE` for the `curl|bash`-distributed installer.
- **CI Structural Validation**: Added a `validate` job to `agent-gates.yml` that parses all JSON, enforces a single canonical version across artifacts, and rejects stale version strings and the wrong `prisma.schema` filename.
- **Audit Trail Clarification**: Documented `audit.jsonl` as a local per-machine trail (gitignored) with no cross-machine immutability guarantee.
- **AI Safety Wiring**: Referenced `config.json -> ai_safety` input sanitization from `AGENTS.md §4`.

### Changed
- **Canonical Version Source**: All version strings now derive from `config.json -> core_version` (`4.3.3`). Synced `AGENTS.md` title, `README.md` header/body/badges, `install.sh`, `install.ps1`, `TASK_TEMPLATE.md`, and the CI workflow name.
- **Unified Branch Convention**: Standardized on Conventional Branching `<type>/issue-<N>-<slug>` across `config.json`, `AGENTS.md`, and `devops-manager/SKILL.md`, replacing the inconsistent `task/` vs `feat/issue-` mix.
- **Platform-Conditional Secrets**: `env-required.json` now marks Gitea credentials as optional (GitHub-only repos no longer fail validation for missing Gitea vars) and adds runtime vars (`NODE_ENV`, `PORT`).
- **Prisma Filename**: Corrected `prisma.schema` → `schema.prisma` in `schema.md` and `system-architect/SKILL.md`.
- **Hermes Learning Targets**: Unified the persistence target set across `AGENTS.md §7` and `soul.md` (`skills/`, `rules.md`, `schema.md`).
- **Slash Commands**: Unified the command list between `AGENTS.md §8` and `README.md` (`/goal`, `/plan`, `/grill-me`, `/teamwork-preview`, `/learn`).
- **Section Numbering**: Fixed non-sequential headers (`2.5`, `3.5`) in `common/utils.md`.
- **Config Hygiene**: Removed dead `retries.rollback_distinct_approaches`; replaced misleading `backup_rotation_count: 3` with `backup_extension: ".bak"` reflecting the single-backup reality.

### Fixed
- **MCP Config Leak**: Replaced the hardcoded internal IP in `mcp_config.json` `GITEA_HOST` with the `${GITEA_HOST}` placeholder.
- **Stale `.gitignore`**: Removed the obsolete `.agents/brain/state.json` ignore line (artifact is FORBIDDEN, not merely ignored) and added `*.bak` coverage.
- **README Directory Tree**: Corrected `TASK_TEMPLATE.md` location (`.agents/`, not root) and added `LICENSE`/`CHANGELOG.md`.
- **Stale Scratch Artifact**: Removed lingering `release_notes.txt` (v4.1.4) from `.agents/scratch/`.
- **`schema.md` Staleness**: Refreshed "Last Verified" date.

## [4.3.2] - 2026-07-28

### Added
- **MCP-First Priority Fallback**: Established a strict Platform Interaction Priority Fallback (Priority 1: MCP, Priority 2: CLI, Priority 3: Human Report) to maximize AI-native API interactions before falling back to CLI.
- **Git Conventional Standards**: Enforced Git Conventional formats for all Issue Titles (`feat: ...`, `fix: ...`) and required professional, highly detailed Issue Bodies (Description, Acceptance Criteria).
- **PR-First Workflow**: Prohibited direct merges to `main`. Enforced `gh pr create` and `gh pr merge` as the mandatory integration pathway.

### Fixed
- **Issue ID Hallucination**: Added an explicit Anti-Hallucination Gate prohibiting the agent from guessing or hallucinating Issue IDs. The agent MUST empirically verify or create issues via CLI/MCP.
- **Continuous Release Syncing**: Ensured every merged PR triggers a mandatory update to `CHANGELOG.md` and a new version bump / GitHub release.

## [4.3.1] - 2026-07-28

### Added
- **Standard Issue-Driven Git Workflow**: Added strict standard flow enforcing: `Create Issue` $\rightarrow$ `Create Branch` $\rightarrow$ `Conventional Commit` $\rightarrow$ `Push` $\rightarrow$ `Merge` $\rightarrow$ `Clean Branch`.
- **Gitea Timetracking Integration**: Enforced accurate timetracker updates for every Gitea issue upon completion.
- **Single Active Plan Priority**: Introduced timestamp-based prioritization for `.agents/plans/*.md` to eliminate context switching amnesia.

### Changed
- **Humanized Skill Modules**: Completely refactored all internal AI skill modules (`code-engineer`, `devops-manager`, `quality-assurance`, `security-docs-auditor`, `system-architect`, `system-janitor`) to replace robotic/imperative instructions with a natural, collaborative "Senior Engineering Co-Pilot" persona.
- **Strict Pre-Execution Gates & Token Efficiency**: Rewrote `AGENTS.md` to aggressively enforce pre-execution issue/plan gates (HARD STOP). Compacted the directive to under 60 lines with a strict $\le 150$ characters per line limit to maximize context token efficiency.
- **Clean Markdown Standards**: Removed messy inline math formatting from `devops-manager/SKILL.md` in favor of standard markdown lists.

### Fixed
- **Plan File TOCTOU Race Conditions**: Fixed state loss vulnerabilities by mandating POSIX Directory Locks for plan files prior to modification.
- **Atomic Backup Safety**: Hardened `replace_file_content` updates by enforcing strict `cp` shell backups before any plan writes.

## [4.3.0] - 2026-07-28

### Added
- **Task-Driven Execution Protocol (`.agents/plans/*.md`)**: Transitioned from volatile state pointers to file-backed micro-task checklists as the Single Source of Truth, enabling zero-amnesia session recovery.
- **Humanized Senior Co-Pilot Persona (`soul.md`)**: Upgraded agent persona to embody an authentic, warm, senior engineering partner with zero-yes-man technical firmness.
- **Zero-Assumption System State Schemas (`schema.md`)**: Defined explicit structural data contracts for `.agents/plans/<task-slug>.md`, `.agents/locks/<hash>.lock/owner.json`, and `.agents/brain/audit.jsonl`.
- **Session Boot Anti-Amnesia Pre-Checks (`AGENTS.md`)**: Hardened memory recovery to run direct filesystem scans and empirical test verification before executing uncompleted micro-tasks.
- **Docker / Podman Gitea MCP Integration**: Aligned Gitea MCP server setup with [gitea.com/gitea/gitea-mcp](https://gitea.com/gitea/gitea-mcp) stdio specification using container runner (`gitea/gitea-mcp:latest`) with `GITEA_HOST` and `GITEA_ACCESS_TOKEN`.
- **POSIX Directory-Based Mutex Locks (`.agents/locks/`)**: Implemented atomic directory creation (`mkdir -p .agents/locks/<md5_hash_of_filepath>.lock`) with `owner.json` metadata and 60-second auto-expiration to resolve TOCTOU race conditions across parallel subagent executions.
- **Mandatory Swarm Triggers**: Added explicit triggers in `AGENTS.md` and `config.json` requiring Orchestrator subagent spawning for multi-file audits ($\ge 3$ files) and multi-domain tasks.
- **Decisions & `/grill-me` Ledger**: Introduced mandatory `## 1. Decisions & Architectural Trade-offs` section in task plans to freeze user directives, design choices, and `/grill-me` interview logs directly to disk.
- **Strict Pre-Execution Hard-Lock Gate**: Prohibited any source code edits until (1) a granular plan file exists in `.agents/plans/` AND (2) a dedicated Git branch (`task/<slug>`) is created.
- **Zero-Batching & Empirical Verification Gate**: Enforced single micro-task execution per turn with mandatory physical CLI output (`exit code 0` from `npm test` or `tsc`) before marking tasks `- [x]`.
- **Empirical Artifact Pre-Check & Auto-Backup (`.bak`)**: Added plan file `.bak` backup protection and full empirical test checks on existing files during session boot to prevent redundant code execution.
- **Git Merge Conflict & Rebase Protocol**: Added strict `git rebase main` requirements in `devops-manager` prior to testing, prohibiting merge conflict markers (`<<<<<<< HEAD`) from reaching source code.
- **Stale Lock Pruning Protocol**: Added automated `owner.json` timestamp scanning in `system-janitor` to purge locks older than 60 seconds.

### Changed
- **Gitea Token & Host Standardization**: Renamed legacy `GITEA_PAT` to official `GITEA_TOKEN` and added explicit `GITEA_HOST` across `.env`, `.env.example`, `mcp_config.json`, and `env-required.json`.
- **Optimized Core Directive Length**: Refactored `AGENTS.md` to 153 lines per Google Antigravity Best Practices to maximize LLM attention window performance and eliminate context token bloat.
- **Symmetrical Tiered Execution Thresholds**: Refactored execution tier criteria to Tier 1 (< 50 lines single file), Tier 2 ($\ge$ 50 lines or multi-file), and Tier 3 (> 100 lines or core architecture refactors).
- **Skill Core Version Decoupling**: Updated all 6 core domain skills (`code-engineer`, `system-architect`, `quality-assurance`, `devops-manager`, `security-docs-auditor`, `system-janitor`) to require core version `>=4.3.0`.
- **Installer Script Scaffolding**: Updated `install.sh` and `install.ps1` to automatically create `.agents/locks/` scaffolding during one-line installations and completely purged obsolete `state.json` reset logic.

### Fixed
- **Manifest Complete Consistency**: Added `audit.jsonl`, `env-required.json`, and `mcp_config.json` explicitly to `AGENTS.md` Complete Directory Manifest.
- **Legacy Interactive Syntax Removal**: Replaced deprecated `ask_question` function calls in `devops-manager/SKILL.md` with natural agent conversation directives.
- **Orphan Scratch Context Leakage**: Resolved context confusion across session switches by enforcing autonomous purging of orphan ephemeral files in `.agents/scratch/` during Session Boot.
- **TOCTOU Race Condition in Parallel Subagents**: Fixed file locking race conditions by replacing file-level JSON mutations with atomic POSIX directory creation using MD5 filepath hashing.

### Removed
- **Legacy `state.json` Persistence File**: Completely eliminated `.agents/brain/state.json` and its schema references from `schema.md`, `AGENTS.md`, and `README.md`, deprecating volatile state tracking.
- **Obsolete Config & Registry Files**: Removed deprecated `"task_claim_lock"` key from `config.json` and purged duplicate `mcp-registry.json` file.

## [4.2.1] - 2026-07-27


### Added
- **Automated Rollback & Recovery Protocol**: Added Section 6.5 to `AGENTS.md` enforcing automatic hard resets (`git reset --hard HEAD` / worktree purge) and post-mortem incident generation after 2 consecutive test verification failures.
- **Parallel File Locking Protocol (Mutex)**: Added Section 5.3 to `AGENTS.md` requiring subagents to claim explicit file-level path locks in `state.json -> claimed_tasks` to prevent write collisions during parallel execution.
- **Framework-Specific Detection & Adaptation**: Added Section 3.5 to `.agents/common/utils.md` for explicit stack rules covering React/Next, Vue/Nuxt, Svelte, Django, FastAPI, Flask, Express, NestJS, Spring Boot, and ASP.NET Core.
- **MCP Health Check & Primary Protocol**: Formalized MCP health ping on startup and graceful fallback chain (MCP -> Native Git -> User Prompt).

## [4.2.0] - 2026-07-27


### Added
- **Multi-Agent Execution Topologies**: Introduced Parallel Swarm Topology (for independent multi-domain audits) and Sequential Pipeline Topology (stage-gated dependency ordering for architecture, development, and QA).
- **Synchronization Barriers & Mutex Task Locking**: Guaranteed zero-skipped responses for concurrent subagents via `claimed_tasks` mutexing and Orchestrator execution freezing until all subagents finish.
- **Universal Polyglot & Legacy Framework Detection**: Expanded `utils.md` and `code-engineer` skill to idiomatically support 14+ language ecosystems (TypeScript, JavaScript, Python, Go, Rust, PHP, Java/Kotlin, C#/.NET, Dart/Flutter, C/C++, Swift, Elixir, and legacy ASP/VB6).
- **Human-Centric Engineering Co-Pilot Persona**: Overhauled `.agents/brain/soul.md` to embody a warm, friendly Senior Partner persona who is uncompromisingly firm on code quality and zero "Yes-Man" pushback.
- **5-Dimension Performance Profiling**: Upgraded `quality-assurance` skill to profile CPU execution, File & Network I/O, Database connection pooling, Heap memory leaks, and historical baseline tracking via `.agents/brain/perf-baseline.json`.

### Changed
- **6 Core Domain Skills Consolidation**: Streamlined 15 redundant skill directories into 6 high-precision core domain skills (`code-engineer`, `system-architect`, `quality-assurance`, `devops-manager`, `security-docs-auditor`, `system-janitor`), reducing initial token bloat by >60%.
- **Google Antigravity Standard Alignment**: Formalized `AGENTS.md` as the supreme workspace directive, defining strict precedence over project-specific `GEMINI.md` files.

### Fixed
- **Hardcoded Credential Redaction**: Fully remediated hardcoded secrets in `.agents/mcp_config.json` and `.env` using environment variable substitution (`${GITHUB_PAT}`, `${GITEA_PAT}`).
- **Anti-Snippet Tunnel Vision**: Explicitly prohibited inferring data structures from truncated snippets; enforced full symbol definition inspection.

## [4.1.4] - 2026-07-25


### Added
- **Task Entrypoint SOP**: Introduced `.agents/TASK_TEMPLATE.md` to force agents to explicitly check off pre-flight and execution requirements before coding, addressing behavioral eagerness.

### Fixed
- **State Initialization Bypass**: Injected a `CRITICAL ENFORCEMENT` rule at the very top of `AGENTS.md` and created default `.agents/brain/state.json` and `.agents/brain/audit.jsonl` files to resolve agents silently skipping the State Management Protocol.
- **Full Audit Fixes (Priority 1-4)**:
  - Added State Lock Protocol and State Recovery Mechanism to prevent corruption.
  - Added Token Budget Management to prevent context window bloat.
  - Added Orchestration Deadlock Detection to prevent infinite recursive loops.
  - Added Prompt Injection Sanitization for `ask_question` inputs.
  - Added MCP Plugin Verification and Degradation Protocol for service unavailability.
  - Enhanced all 9 skills with audit recommendations (Provenance Verification, Rollback Verification, Memory Leak Protocols, CI Integration, Mobile Accessibility Tests).
- **Hermes Protocol & Self-Learning**:
  - Implemented the Hermes Protocol in `AGENTS.md` to distinguish between static rules and dynamic procedural skill generation.
  - Forced agent auto-learning by injecting `rules.md` loading into `TASK_TEMPLATE.md` Pre-flight checklist.
  - Generated new `branch-janitor` skill autonomously to handle cleanup of stale local/remote branches.
  - Generated `polyglot-developer` and `advanced-debugger` skills to enforce language-agnostic clean code standards and scientific debugging methods.
  - Generated `ci-cd-specialist`, `data-synthesizer`, and `context-optimizer` to complete the 15-module Elite Enterprise architecture (handling pipelines, mock data, and token bloat compression).

## [4.1.3] - 2026-07-23

### Fixed
- **Supply Chain Security**: Pinned GitHub Actions (`actions/checkout` and `gitleaks-action`) to full 40-character commit SHAs instead of mutable tags (`@v4`, `@v2`) to resolve Semgrep SAST blocking findings.

## [4.1.2] - 2026-07-23

### Added
- **Server-Side Enforcement**: Scaffolding for GitHub Actions `.github/workflows/agent-gates.yml` to enforce CI/CD checks (Gitleaks, Semgrep) at the server level, preventing manual bypasses.
- **RAG/Vector Brain Support**: Formalized the requirement in `AGENTS.md` to prioritize RAG or Vector-Based MCP integrations over legacy paginated reads for enterprise scalability.

### Changed
- **Worktree Rollback Protocol**: Upgraded the agent's safe abort protocol from `git stash` to `git worktree add`, enabling safe isolation and immediate discarding of ephemeral corrupted states.

## [4.1.1] - 2026-07-23

### Fixed
- **Security Baseline Compliance**: Created missing `.agents/brain/env-required.json` to formally document environment variables and resolve architecture/security auditor warnings.

## [4.1.0] - 2026-07-23

### Added
- **New Agentic Skills**: Introduced `test-engineer`, `documentation-engineer`, and `performance-profiler` for comprehensive lifecycle management.
- **Centralized Configuration**: Moved timeouts, retries, trust metrics, and viewports into a single `.agents/config.json`.
- **Shared Utilities**: Created `.agents/common/utils.md` for framework discovery, API version negotiation, and log redaction.
- **Skill Version Decoupling**: Skills now declare compatibility via `requires_core` frontmatter, decoupled from hardcoded core directives.
- **Safe Abort Protocol**: Replaced destructive resets with safe git stashing during timeout aborts (`git stash push -u -m "agent-abort-backup-<timestamp>"`).
- **Log Redaction**: Automatic regex-based redaction of secrets in `audit.jsonl` and mandatory log rotation.
- **API Version Negotiation**: Added fallback mechanisms and version checks for external tools (MCP, Gitea, GitHub).
- **Just-In-Time Manifest Verification**: Dynamically validates `SKILL.md` hashes against expected signatures via `sha256sum`.

### Changed
- **Optimized Context Window (MVC)**: Severely truncated `AGENTS.md` and pruned universal software engineering concepts from skill files, significantly reducing context bloat and improving execution accuracy.
- **State Locking Stability**: Replaced advisory locking (`flock`) with atomic writes (`.tmp` to `.json`) for `.agents/brain/state.json`.
- **Orchestration Concurrency**: Paralleled independent audit skills (`ui-a11y-reviewer` and `performance-profiler`).
- **Merge Gate Hardening**: Substring matching replaced with an explicit `/merge-confirm <ticket>` command requirement.
- **Supply Chain Trust Checks**: Enforced objective metrics (downloads, stars, age) against `.agents/config.json` before installing dependencies via `npm audit` and `safety check`.
- **SAST & Secret Scanning Robustness**: Mandated `npx gitleaks` fallback, cached SAST checks, and explicit tool availability validations (`which`/`npx`).
- **Time Tracking Override**: Formalized "proceed without tracking" to prevent workflow blockage while maintaining incident documentation.
- **Quick Branch Pattern**: Replaced ambiguous quick mode prefixing with explicit `<prefix>/quick-<slug>` format.

### Fixed
- Addressed infinite recursion deadlocks between `schema-manager` and `architecture-auditor` by enforcing a maximum of 1 re-audit cycle.
- Fixed broken section references across all skill files, making references to `AGENTS.md` context-independent.
- Clarified UI responsiveness automated checks requiring `Puppeteer/Playwright` and fixed blind spots in consumer vs. admin review criteria.

## [4.0.0] - 2026-07-22

### Added
- **Supreme `AGENTS.md` Constitution**: A single source of truth that governs all sub-agents and operations, strictly superseding any individual skill configurations.
- **Skill-Based Modular Architecture**: Introduced a dynamic skill execution system stored in `.agents/skills/`, replacing legacy bash scripts.
- **6 Core Quality & Safety Skills**:
  - `git-workflow`: Enforces Branch -> Commit -> PR lifecycle and manages Gitea time tracking.
  - `architecture-auditor`: Enforces holistic impact analysis and blast radius checks.
  - `schema-manager`: Manages DB schemas, migrations, and eliminates hallucinated fields.
  - `ui-a11y-reviewer`: Branches logic between Consumer (premium aesthetic) and Admin (data density) views, while enforcing WCAG.
  - `execution-manager`: Discovers package managers dynamically, prevents redundancy, and enforces ephemeral execution (`npx`, `pnpm dlx`).
  - `security-observability-auditor`: Mandatory SAST, secret scanning (`gitleaks`), and structured observability (JSON/Prometheus) enforcement.
- **Automated Rollback Protocol**: A strict 3-strike rule that forces the agent to snapshot (`git stash`), document the incident in `.agents/incidents/`, revert to a known good state, and validate via linters/smoke tests before escalating.
- **Zero-Assumption Policy**: Prohibits agents from guessing database fields or API contracts without explicit verification.
- **Token Optimization & Verification**: Rules to limit context window bloat via paginated reading (`StartLine`/`EndLine`). Clarified that partial reads are only valid if they capture full structural blocks.
- **MCP Dynamic Discovery & Configuration**: Introduced `.agents/brain/mcp-registry.json` for dynamic discovery, and `.agents/mcp_config.json.example` demonstrating correct GitHub Copilot SSE and HTTP-based Gitea integrations.
- **Git Hygiene & Scaffolding**: Deployed `.gitignore` to prevent credential/state leakage (e.g., ignoring `.agents/scratch/`), alongside `.gitkeep` placeholders and baseline templates (`schema.md`, `rules.md`) to guarantee exact directory replication upon cloning.
- **Strict `!quick` Mode**: A specific bypass command that skips Issue generation and PR overhead but strictly maintains branching (`quick-`), atomic commits, and merge approval gates.
- **Merge Conflict Resolution Protocol**: Specific guidance for regenerating lock files (`yarn.lock`, `poetry.lock`, `go.sum`, etc.) from `main` to break loops.
- **5-Minute Inactivity Timeout**: If the user does not respond to `ask_question` within 5 minutes, agents will stop trackers, log incidents, notify the user, and abort safely.

### Changed
- **Deprecated `helper.sh` and `validate.py`**: Transitioned entirely to AI-native rule evaluation via the `security-observability-auditor` and `git-workflow` skills.
- **Escalation Rules**: Refined tool boundary definitions; `ask_question` is for workflow/architectural choices, while `ask_permission` is strictly for OS-level EACCES/EPERM errors.
- **Hotfix Testing**: Exempted `hotfix/` branches from 80% coverage gates, reducing them to 60% with mandatory manual QA, but maintaining strict SAST execution requirements.

### Removed
- Removed legacy bash-based pre-commit hooks and mutex locks in favor of direct agent workflow constraints.

---

## [3.153.2] - Previous Legacy Version
*See v3 documentation for older changes prior to the AAC V4 Agentic Architecture migration.*
