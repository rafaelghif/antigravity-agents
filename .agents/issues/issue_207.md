---
id: issue-207
title: "Harden Git-based installation, interactive setup interview, zero-touch execution loop, and comprehensive README documentation"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to ensure that:
1. Installation is natively done from the Git repository.
2. Bootstrapping interviews the user at the very beginning about infrastructure, database, and frameworks, writing them to the workspace-level schema blueprint.
3. The agent is strictly guided by self-correcting Lookahead Loops and Zero-Touch Chaining rules to reduce user interactions and eliminate hallucinations.
4. Comprehensive documentation is updated in `README.md`.

## Tasks
- [x] Harden `install.sh` to clone natively from Git <!-- id: task-install-sh -->
- [x] Harden `install.ps1` to clone natively from Git <!-- id: task-install-ps1 -->
- [x] Update `schema.md.template` to include DB, infra, and framework placeholders <!-- id: task-schema-template -->
- [x] Update `bootstrap.py` to prompt for and parse DB, infra, and framework parameters <!-- id: task-bootstrap-py -->
- [x] Update `AGENTS.md` with Lookahead Loop and Zero-Touch rules <!-- id: task-agents-rules -->
- [x] Update active `rules.md` and `rules.md.template` with Lookahead Loop and Zero-Touch rules <!-- id: task-rules-md -->
- [x] Update `README.md` with complete installation, versioning, and commands documentation <!-- id: task-readme-docs -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Installers clone repository natively from Git using `git clone --depth 1`.
- [x] Bootstrap prompts for database, infrastructure, and framework at the start and writes them to `.agents/schema.md`.
- [x] `AGENTS.md` and rules contain Lookahead Loop and Zero-Touch chaining rules.
- [x] `README.md` documents all features, versioning, setup, and CLI commands completely.
- [x] All unit tests pass successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [install.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.sh)
  - [install.ps1](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.ps1)
  - [bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py)
  - [schema.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/schema.md.template)
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
  - [rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [README.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/README.md)
- Active module locks:
  - `bootstrap`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
