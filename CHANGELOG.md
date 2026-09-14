# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0] - 2026-09-14

### Major Paradigm Shift: Native Google Antigravity 2.0 Architecture
Version 5.0.0 is a complete rewrite and architectural evolution, moving from custom Python harness scripts (v4 AAC) to first-class, native **Google Antigravity Customization Architecture**:

### Added
- **Gemini 3.8 Flash (High) Pairing Directives**: Optimized root [`AGENTS.md`](file:///D:/Project/antigravity-agents/AGENTS.md) adhering to the **Caveman Principle** (terse, fluff-free technical precision) and **Ponytail Principle** (7-rung minimalist code ladder).
- **Progressive Disclosure Skills**: Integrated all 64 modular skills in `.agents/skills/` across testing, architecture, planning, code review, and token reduction:
  - `ponytail` suite (minimalist code ladder, audit, debt, review).
  - `caveman` suite (ultra-compact token conservation and subagent output).
  - `mattpocock` suite (`ask-matt`, `to-spec`, `to-tickets`, `tdd`, `code-review`, `wayfinder`, `triage`, `grilling`, `domain-modeling`).
- **5-Tier Memory Architecture & Cross-Session Protocol**: Implemented `memory-management.md` rule (`trigger: always_on`), root `CONTEXT.md` living domain glossary, `docs/adr/0001-antigravity-5-tier-memory-system.md`, and standardized session handoff templates with `.scratch/` sandboxing.
- **Multi-Platform Zero-Pollution Installers**:
  - Universal NPX CLI ([`bin/cli.mjs`](file:///D:/Project/antigravity-agents/bin/cli.mjs)): `npx github:rafaelghif/antigravity-agents-core init` or `npx antigravity-agents-core init`.
  - Standalone Windows PowerShell installer ([`install.ps1`](file:///D:/Project/antigravity-agents/install.ps1)): `irm https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.ps1 | iex`.
  - Standalone Linux/macOS installer ([`install.sh`](file:///D:/Project/antigravity-agents/install.sh)): `curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.sh | bash`.
  - **Zero Package.json Pollution Guarantee**: Installers safely scaffold `.agents/`, `AGENTS.md`, and `CONTEXT.md` without ever writing or overwriting `package.json` in user workspaces (protecting Python, Go, Rust, C++, PHP, and existing Node projects).
- **Cross-Platform Node.js Lifecycle Hooks & ADR-0002**:
  - Migrated lifecycle hooks in `.agents/hooks.json` to universal Node.js CommonJS scripts ([`block-dangerous-git.cjs`](file:///D:/Project/antigravity-agents/.agents/hooks/block-dangerous-git.cjs) and [`verify-on-stop.cjs`](file:///D:/Project/antigravity-agents/.agents/hooks/verify-on-stop.cjs)), documented in [`docs/adr/0002-cross-platform-node-lifecycle-hooks.md`](file:///D:/Project/antigravity-agents/docs/adr/0002-cross-platform-node-lifecycle-hooks.md).
  - Ensures seamless hook execution across both Windows (`cmd /c`) and POSIX (`sh -c`) platforms.
- **Automated Verification Suites**:
  - Added unit test suite in [`tests/cli.test.mjs`](file:///D:/Project/antigravity-agents/tests/cli.test.mjs) verifying CLI commands (`init`, `doctor`, `audit`, `list`) and asserting zero `package.json` creation in target directories.
  - Added test suite in [`tests/memory-system.test.mjs`](file:///D:/Project/antigravity-agents/tests/memory-system.test.mjs) verifying memory architecture and 64-skill compliance.
- **Antigravity Native Lifecycle Hooks**: Configured in `.agents/hooks.json` supporting `PreToolUse` (git guardrails) and `Stop` (`quality-gate` running `verify-on-stop.cjs` to prevent exit with failing tests).
- **Git Guardrails Hook**: Intercepts `run_command` in Antigravity to block destructive git operations (`push`, `reset --hard`, `clean -f`, `branch -D`) using cross-platform Node.js ([`block-dangerous-git.cjs`](file:///D:/Project/antigravity-agents/.agents/hooks/block-dangerous-git.cjs)).
- **Autonomous Multi-Agent Subagent Graphs**: Leverages `invoke_subagent` with isolated workspace branches (`Workspace: "branch"` or `"share"`), enabling concurrent implementation of spec task graphs.
- **Multi-VCS Model Context Protocol (MCP)**: Native workspace configuration for **Gitea MCP** (stdio) and **GitHub Copilot MCP** (remote SSE) in `.agents/mcp_config.json`.
- **Workspace Plugins Architecture**: Implemented `.agents/plugins/workspace-integrations/` packaging workspace-scoped MCP servers and sidecars, registered via explicit `.agents/plugins.json` and `.agents/skills.json`.
- **Background Sidecars Engine**: Integrated persistent background runner architecture (`sidecar.json`) with an automated repository health and branch hygiene monitor (`repo-health`).
- **Complete 64-Skill Compliance Audit**: Verified all 64 skills against 8 Antigravity operational dimensions across 7 task batches, tracked in `docs/audit-checklist-64-skills.md` (512 checks passing, 100% compliant).
- **Rule Progressive Disclosure Triggers**: Configured `trigger: always_on` across modular rules (`caveman.md`, `coding-standards.md`, `git-workflow.md`, `ponytail.md`, `memory-management.md`).
- **Credential Quarantine**: Added comprehensive `.gitignore` sandboxing for `.agents/mcp_config.json`, `.agents/plugins/**/mcp_config.json`, `.env`, `.scratch/*`, tokens, keys, and PATs, alongside sanitized example templates.
- **Multi-Platform Parity**: Fully tested across Windows PowerShell 5.1+, Windows cmd, macOS, and Linux bash/sh environments.

### Changed
- Refactored all inherited Claude Code specific patterns (`CLAUDE.md`, `.claude/`, generic `Skill` tool calls, `Bash` tool calls) to native Google Antigravity primitives (`AGENTS.md`, `.agents/`, `view_file`, `run_command`, `invoke_subagent`).
- Cleaned and decoupled workspace configurations from machine-global state (`~/.gemini/config/`).

---

## [4.47.2] - 2026-09-13

### Fixed
- **Installer Source Validation & CLI Sandbox Alignment**: Fixed `install.py` aborting during release source validation by passing `--source-only` and decoupling external host CLI settings from source archive validation.
- **Comprehensive Antigravity Settings Sanitizer**: Implemented `sanitize_antigravity_settings` in `scripts/health_check.py`.
- **Consumer Workspace Validation Scope**: Scoped global CLI settings validation in `scripts/validate.py` to framework development runs only.
