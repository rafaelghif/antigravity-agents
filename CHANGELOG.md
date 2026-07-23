# Changelog

All notable changes to the Antigravity Agent Core (AAC) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
