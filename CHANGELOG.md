# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
