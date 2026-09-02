# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.38.2] - 2026-09-01
### Fixed
- AST Guard: Refactored semantic grapher to resolve O(N^2) complexity violations.
- Hooks: Fixed CWD bug in post-invoke hook to resolve false positive CI errors.

## [4.38.2] - 2026-09-01
### Fixed
- Fixed fatal crash in `scripts/semantic_grapher.py` by adding missing `--blast-radius` argument to CLI parser.
- Fixed worker subagent permission blocking in `scripts/strict_delegation_guard.py` to allow editing application code in `/src/`, `/app/`, `/lib/`.
- Repaired neurosymbolic validation payload validation logic.

## [4.38.2] - 2026-09-02
### Fixed
- Ported all bash hooks to Python to prevent CRLF syntax errors on Windows and remove jq dependency.

## [4.38.0] - 2026-09-01
### Added
- Official Google Antigravity Schema Alignment (`config.json` -> `mcp_config.json`).
- Native portability improvements for cross-platform agent injection.
