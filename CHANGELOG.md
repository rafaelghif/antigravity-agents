# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0] - 2026-09-14

### Major Paradigm Shift: Native Google Antigravity 2.0 Architecture
Version 5.0.0 is a complete rewrite and architectural evolution, moving from custom Python harness scripts (v4 AAC) to first-class, native **Google Antigravity Customization Architecture**:

### Added
- **Gemini 3.8 Flash (High) Pairing Directives**: Optimized root [`AGENTS.md`](file:///D:/Project/antigravity-agents/AGENTS.md) adhering to the **Caveman Principle** (terse, fluff-free technical precision) and **Ponytail Principle** (7-rung minimalist code ladder).
- **Progressive Disclosure Skills**: Integrated over 60+ modular skills in `.agents/skills/` across testing, architecture, planning, code review, and token reduction:
  - `ponytail` suite (minimalist code ladder, audit, debt, review).
  - `caveman` suite (ultra-compact token conservation and subagent output).
  - `mattpocock` suite (`ask-matt`, `to-spec`, `to-tickets`, `tdd`, `code-review`, `wayfinder`, `triage`, `grilling`, `domain-modeling`).
- **Antigravity Native Lifecycle Hooks**: Configured in `.agents/hooks.json` supporting `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, and `Stop` events with protojson camelCase contracts.
- **Git Guardrails Hook**: Intercepts `run_command` in Antigravity to block destructive git operations (`push`, `reset --hard`, `clean -f`, `branch -D`) using native PowerShell ([`block-dangerous-git.ps1`](file:///D:/Project/antigravity-agents/.agents/skills/git-guardrails/scripts/block-dangerous-git.ps1)) and Node.js ([`block-dangerous-git.js`](file:///D:/Project/antigravity-agents/.agents/skills/git-guardrails/scripts/block-dangerous-git.js)).
- **Autonomous Multi-Agent Subagent Graphs**: Leverages `invoke_subagent` with isolated workspace branches (`Workspace: "branch"` or `"share"`), enabling concurrent implementation of spec task graphs.
- **Multi-VCS Model Context Protocol (MCP)**: Native workspace configuration for **Gitea MCP** (stdio) and **GitHub Copilot MCP** (remote SSE) in `.agents/mcp_config.json`.
- **Credential Quarantine**: Added comprehensive `.gitignore` sandboxing for `.agents/mcp_config.json`, `.env`, tokens, keys, and PATs, alongside a sanitized [`mcp_config.example.json`](file:///D:/Project/antigravity-agents/.agents/mcp_config.example.json).
- **Windows PowerShell 5.1+ Parity**: Fully tested for Windows PowerShell command execution (strictly replacing `&&` with `;`).

### Changed
- Refactored all inherited Claude Code specific patterns (`CLAUDE.md`, `.claude/`, generic `Skill` tool calls, `Bash` tool calls) to native Google Antigravity primitives (`AGENTS.md`, `.agents/`, `view_file`, `run_command`, `invoke_subagent`).
- Cleaned and decoupled workspace configurations from machine-global state (`~/.gemini/config/`).

---

## [4.47.2] - 2026-09-13

### Fixed
- **Installer Source Validation & CLI Sandbox Alignment**: Fixed `install.py` aborting during release source validation by passing `--source-only` and decoupling external host CLI settings from source archive validation.
- **Comprehensive Antigravity Settings Sanitizer**: Implemented `sanitize_antigravity_settings` in `scripts/health_check.py`.
- **Consumer Workspace Validation Scope**: Scoped global CLI settings validation in `scripts/validate.py` to framework development runs only.
