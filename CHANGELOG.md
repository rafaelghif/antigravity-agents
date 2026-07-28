# Changelog

All notable changes to the Antigravity Agent Core (AAC) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
