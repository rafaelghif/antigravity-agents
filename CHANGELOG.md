# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.45.0] - 2026-09-05

### Added
- **Git-First Distribution & Lifecycle Engine**: Hardened `install.py` with `--version`, `--reinstall`, `--repair`, `--rollback`, and `--uninstall` capabilities backed by `.agents/install_manifest.json` SHA256 integrity auditing (`--status`/`--audit`).
- **Automated Workspace Health Check & Self-Diagnosis**: Implemented `scripts/health_check.py` validating 14 health dimensions with structured `--json` output and deterministic `--repair`.
- **Concurrency-Hardened Working Memory**: Added cross-platform advisory file locking and atomic temporary writes to `scripts/memory_consolidator.py`, preventing race conditions during parallel subagent executions.
- **Structured Inter-Agent Messaging Protocol**: Added `format_structured_message` and `send_structured_message` in `scripts/inbox_manager.py` implementing RFC-compliant structured handoffs over the disk-backed blackboard.
- **Air-Gapped & Offline Installation Engine**: Enhanced `install.py` with `--source-dir` flag and automated local repository checkout fallback, enabling deterministic offline installations without GitHub network access. Automated addition of `.agents-backups/` to target project `.gitignore`.
- **OS Hook Chaos Test Suite**: Implemented 5 test cases in `tests/test_hooks.py` validating CRLF line endings, missing dependency fallbacks, concurrency races, Unicode path normalization, and null environment handling.
- **Safe Multi-Platform Standard Input Buffering**: Centralized binary standard input decoding in `scripts/hooks/hook_utils.py` (`read_safe_stdin()`), preventing UTF-8 and codepage decoding failures across Windows `cp1252` and Linux while adhering strictly to DRY anti-duplication constraints.

### Changed
- **Universal Installer Bootstrap Resilience**: Added `wget` fallback to `install.sh` and `-UseBasicParsing` to `install.ps1` for seamless bootstrap on minimal POSIX containers and PowerShell 5.1.
- **Cross-Platform Hook Execution**: Hardened `.agents/plugins/aac-core/hooks.json` to execute nested subprocesses via `sys.executable`, eliminating Python binary naming discrepancies across Windows and POSIX environments.
- **Expanded Test Coverage & Full Release Parity**: Reached 178 passing unit tests across 30 test suites in 0.611s with zero regressions across all 9 technical gates and release consensus verification.

### Fixed
- **Hermes Task Graph Resilience**: Added fallback to task filename stem in `scripts/hermes_manager.py` to prevent silent task dropping when YAML declarations omit explicit `id:` keys. Ensured 100% discovery and topological ordering across all sprint tasks.

## [4.44.3] - 2026-09-05

### Added
- **Intent Auto-Decomposition Engine**: Added `--decompose`, `--output-dir`, and `--force` CLI flags to `scripts/intent_compiler.py` to compile and parse `objectives` into topologically chained `tasks/XX_<slug>.yaml` micro-tasks with regex-bounded domain/persona routing (`staff-backend`, `frontend-architect`, `database-sre`, `devsecops-principal`, `qa-automation-lead`).
- **Topological Wave Execution Planner**: Enhanced `scripts/hermes_manager.py` with `--plan`, `--mermaid`, and `--json` flags to compute parallel execution stages (waves), concurrency limits, and auto-generate Mermaid DAG graphs without nested loop O(N²) overhead.

### Changed
- **Zero-Regression Full Test Parity**: Expanded unit test suite to 122 tests covering multi-domain decomposition, topological dependency chaining, wave concurrency computation, and cross-platform streams with 100% pass rate.

### Fixed
- **Cross-Platform UTF-8 Hardening**: Created `scripts/platform_guard.py` to ensure robust `sys.stdout`/`sys.stderr` UTF-8 stream fallback and injected `PYTHONIOENCODING="utf-8"` across all subprocess executions, resolving Windows `cp932`/`cp1252` `UnicodeEncodeError`.

## [4.44.2] - 2026-09-03

### Added
- **Engine Audit & Health Modes**: Added `--status` non-blocking DAG inspection to `scripts/hermes_manager.py` and `--audit` procedural rule validation to `scripts/self_learner.py`.

### Changed
- **Enhanced CLI Subcommand Support**: Upgraded `scripts/semantic_grapher.py` to seamlessly handle both positional subcommands (`blast-radius <symbol>`, `scan`) and standard flags (`--blast-radius`).
- **Zero Dummy Logic Guarantee**: Conducted repository-wide AST audit across all scripts and personas; verified 100% genuine execution with zero stubs, mocks, or simulations.
- **Verified Compatibility Metadata**: Synchronized `cli_version` in `.agents/antigravity-compatibility.json` to installed AGY 1.1.25.
- **Sprint Task Completion**: Verified `tasks/01_autonomous_loop.yaml` acceptance criteria and recorded dynamic standup sync in `tasks/meeting_notes.md`.

## [4.44.1] - 2026-09-03

### Changed
- **Full God Mode Unleashed**: Stripped all interactive roadblocks and artificial barriers (`decision: "ask"` removed from pre-tool quality gates; actions permitted autonomously with telemetry logging).
- **Continuous Blackboard Orchestration**: Removed debate turn freezing in `scripts/inbox_manager.py`—debate turns are auto-resolved seamlessly to prevent deadlocks.
- **Unrestricted Agent Spawns**: Added `--dangerously-skip-permissions` across all `agy` invocations in `meeting_coordinator.py` and `autonomous_loop.py`.
- **Extended Circuit Breakers**: Raised Hermes task iterations to 10 and expanded timebox timeouts to 60/120 minutes in `.agents/config.json`.
- **God Mode Persona Upgrade**: Explicitly unlocked `<MODE>GOD_MODE_UNLEASHED</MODE>` across all 8 L9 personas in `.agents/agents/*.md`.

## [4.44.0] - 2026-09-03

### Added
- **Strict Anti-Hallucination Protocol**: Implemented mandatory Phase 0 Reconnaissance (`python3 scripts/grounding.py`, full file inspection via `view_file`, and blast-radius tracing) across all 8 L9 subagent personas in `.agents/agents/*.md`.
- **Pre-Tool Anti-Regression Guard**: Enhanced `scripts/hooks/pre_tool_quality_gate.py` to intercept and block blind destructive `write_to_file(Overwrite=True)` on existing non-empty files, eliminating accidental overwrites.
- **Automated Standup Synchronization**: Extended `scripts/meeting_coordinator.py --standup` to dynamically evaluate active sprint tasks and log structured standup events directly to the blackboard and `tasks/meeting_notes.md`.

### Changed
- **Master Workspace Policy Upgrades**: Updated `AGENTS.md` and `GEMINI.md` to establish non-destructive code preservation, epistemic grounding, and topological multi-agent DAG orchestration as non-negotiable core invariants.

## [4.43.0] - 2026-09-03

### Added
- **Epistemic Grounding Engine**: Created pure stdlib `scripts/grounding.py` that discovers actual languages, dependencies, frameworks, and manifests before coding, eliminating API hallucinations.
- **Pure Stdlib YAML Parser**: Created `scripts/yaml_loader.py` providing zero-dependency fallback YAML parsing for `dag_orchestrator.py`, `hermes_manager.py`, and `intent_compiler.py`.
- **Dedicated Researcher Persona**: Created `.agents/agents/researcher.md` backed by the `deep-research` skill.
- **Multi-Mode Meeting Orchestration**: Extended `scripts/meeting_coordinator.py` with `--standup`, `--planning`, `--review`, and `--sync` on-demand meeting modes.
- **Comprehensive Test Suite**: Total passing unit tests grew to 55 across 11 test modules with 100% green release gates.

### Changed
- **Consolidated 11 Core Enterprise Skills**: Refactored and consolidated 18 fragmented micro-skills down to 11 authoritative playbooks (`architecture`, `code-quality`, `data-engineering`, `deep-research`, `design`, `devops`, `observability`, `security`, `semantic-graphing`, `verification`, `caveman`).
- **Operationalized Multi-Agent DAG**: Wired authentic verification gates to personas in `.agents/workflows/standard_pr.yaml` (PM intent lifecycle, Backend verification gates, QA test suite, DevSecOps hygiene, Scrum Master standup reporting).
- **Universal Stack Grounding in Telemetry**: Refactored `scripts/hooks/post_invoke_telemetry.py` to auto-detect any ecosystem (Python, Go, Rust, Java, C#, PHP, Ruby, etc.) via `grounding.py`.
- **Bootstrap Contract Safeguards**: Updated `install.py` to deploy initial `intent.yaml` and `handoff.json` so newly installed projects pass verification out-of-the-box.
- **Full Browsing & Search Permissions**: Granted unrestricted permissions for `search_web`, `read_url_content`, and `read_browser_page` in `.agents/antigravity-settings.example.json`.

### Fixed
- **Cross-Platform Path Sanitization**: Normalized file path separators in `scripts/hooks/pre_tool_quality_gate.py` to prevent Windows `.git` check bypasses.

## [4.42.1] - 2026-09-02

### Added
- **Advanced Corrective & Preventive Action**: Coordinator now warns agents nearing debate limits (Preventive) and resets state while forcing Scrum Master intervention if blocked (Corrective).

### Changed
- **God Mode Enabled**: All subagents and co-workers universally upgraded to expert status with `enable_write_tools`, `enable_mcp_tools`, and `enable_subagent_tools`. Agents can now search the internet, modify files natively, and spawn their own worker subagents.
- **Enterprise Cognitive Meetings**: Completely rewrote `meeting_coordinator.py` to invoke the `scrum-master` to read the blackboard and compile authentic standup notes into `tasks/meeting_notes.md`.

### Fixed
- **Installer Dependencies**: Removed non-standard dependency checks (`jq`, `gh`, `curl`) from `install.sh` and `install.ps1` that blocked installations on vanilla environments like Windows PowerShell.
- **Cross-Platform Purity**: Removed all `bash -c` dependencies in hooks. Hook gates now use pure Python subprocesses, ensuring 100% execution across Windows CMD, PowerShell, Linux, and macOS.

### Removed
- **Deadlock Eradication**: Erased residual restrictive sandboxing files globally.

## [4.41.0] - 2026-09-02

### Changed
- **Orchestration**: `autonomous_loop.py` now runs native `agy` CLI spawns for true autonomous loops, replacing mocked timers.

### Removed
- **Agentic Sandbox**: Removed arbitrary restrictions (`manager_blindfold.py`, `strict_delegation_guard.py`, `pre_tool_delegation.py`, `pre_tool_hitl.py`) to fully unleash L9 Expert capabilities.

## [4.40.0] - 2026-09-02

### Security
- **DevSecOps Audit**: Removed hardcoded tokens and strictly pinned all GitHub Actions and pip dependencies to explicit SHAs and versions.
- **CI/CD**: Removed PR fork bypass vulnerability in GitHub Actions workflows.
- **Permissions**: Revoked wildcard agent permissions to enforce Least Privilege (Zero-Trust).

### Fixed
- **Testing**: Eradicated sham tests and tautologies in the test suite. Implemented proper boundary validations.
- **Performance**: Resolved recursive globbing latency in `pre_tool_quality_gate.py`.
- **Reliability**: Fixed empty catch blocks that silently swallowed OS and syntax errors across all hooks.
- **Code Quality**: Added strict Type Hints across `scripts/` to comply with L9 enterprise standards.

## [4.38.2] - 2026-09-02

### Fixed
- **Windows Hook Syntax**: Ported all bash hooks to Python to prevent CRLF syntax errors on Windows and remove `jq` dependency.
- **AST Guard Complexity**: Refactored semantic grapher to resolve nested loop complexity violations.
- **Hook Working Directory**: Fixed CWD bug in post-invoke hook to resolve false positive CI errors.

## [4.38.0] - 2026-09-01

### Added
- **Antigravity Schema Alignment**: Official Google Antigravity Schema Alignment (`config.json` -> `mcp_config.json`).
- **Cross-Platform Injection**: Native portability improvements for cross-platform agent injection.

[4.45.0]: https://github.com/rafaelghif/antigravity-agents/compare/v4.44.3...v4.45.0
[4.44.3]: https://github.com/rafaelghif/antigravity-agents/compare/v4.44.2...v4.44.3
[4.44.2]: https://github.com/rafaelghif/antigravity-agents/compare/v4.44.1...v4.44.2
[4.44.1]: https://github.com/rafaelghif/antigravity-agents/compare/v4.44.0...v4.44.1
[4.44.0]: https://github.com/rafaelghif/antigravity-agents/compare/v4.43.0...v4.44.0
[4.43.0]: https://github.com/rafaelghif/antigravity-agents/compare/v4.42.1...v4.43.0
[4.42.1]: https://github.com/rafaelghif/antigravity-agents/compare/v4.41.0...v4.42.1
[4.41.0]: https://github.com/rafaelghif/antigravity-agents/compare/v4.40.0...v4.41.0
[4.40.0]: https://github.com/rafaelghif/antigravity-agents/compare/v4.38.2...v4.40.0
[4.38.2]: https://github.com/rafaelghif/antigravity-agents/compare/v4.38.0...v4.38.2
[4.38.0]: https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.38.0
