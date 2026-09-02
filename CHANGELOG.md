# Changelog

## [4.42.1] - 2026-09-02
### Hotfix: Installer Dependencies
- **Dependency Fix**: Removed hallucinated requirements (`jq`, `gh`, `curl`) from `install.sh` and `install.ps1` that were blocking fresh installations on environments like Windows PowerShell.
## [4.42.1] - 2026-09-02
### Omni-God Mode Unlock & L9 Orchestrator Refactor
- **God Mode Enabled**: All subagents and co-workers universally upgraded to expert status with `enable_write_tools`, `enable_mcp_tools`, and `enable_subagent_tools`. Agents can now search the internet, modify files natively, and spawn their own worker subagents.
- **Enterprise Cognitive Meetings**: Completely rewrote `meeting_coordinator.py`. It no longer just sends "ping" messages. It natively invokes the `scrum-master` to cognitively read the blackboard and compile real standup meeting notes into `tasks/meeting_notes.md`.
- **Advanced Corrective/Preventive Action**: Coordinator now warns agents nearing debate limits (Preventive) and resets state while forcing Scrum Master intervention if blocked (Corrective).
- **Cross-Platform Purity**: Removed all `bash -c` dependencies in hooks. Hook gates now use pure Python subprocesses, ensuring 100% flawless execution on Windows CMD, PowerShell, Linux, and Mac.
- **Deadlock Eradication**: Erased all residual restrictive sandboxing files globally.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.41.0] - 2026-09-02
### Removed
- **Agentic Sandbox:** Removed arbitrary restrictions (`manager_blindfold.py`, `strict_delegation_guard.py`, `pre_tool_delegation.py`, `pre_tool_hitl.py`) to fully unleash L9 Expert capabilities.
### Changed
- **Orchestration:** `autonomous_loop.py` now runs native `agy` CLI spawns for true autonomous loops, replacing mocked timers.

## [4.40.0] - 2026-09-02
### Security
- **DevSecOps Audit:** Removed hardcoded tokens and strictly pinned all GitHub Actions and pip dependencies to explicit SHAs and versions.
- **CI/CD:** Removed PR fork bypass vulnerability in GitHub Actions workflows.
- **Permissions:** Revoked wildcard agent permissions to enforce Least Privilege (Zero-Trust).

### Fixed
- **Testing:** Eradicated "Sham Tests" and tautologies in the test suite. Implemented proper Mocking and edge-case boundary validations.
- **Performance:** Resolved massive O(N^2) recursive globbing latency in `pre_tool_quality_gate.py`.
- **Reliability:** Fixed empty catch blocks that silently swallowed OS/Syntax errors across all hooks.
- **Code Quality:** Added strict Type Hints across `scripts/` to comply with L9 enterprise standards.

## [4.38.2] - 2026-09-02
### Fixed
- Ported all bash hooks to Python to prevent CRLF syntax errors on Windows and remove jq dependency.
- AST Guard: Refactored semantic grapher to resolve O(N^2) complexity violations.
- Hooks: Fixed CWD bug in post-invoke hook to resolve false positive CI errors.

## [4.38.0] - 2026-09-01
### Added
- Official Google Antigravity Schema Alignment (`config.json` -> `mcp_config.json`).
- Native portability improvements for cross-platform agent injection.
