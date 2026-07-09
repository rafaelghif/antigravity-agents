---
id: issue-229
title: "chore: upgrade project version name and SemVer to V3"
status: open
assignee: corporate-work
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
chore: upgrade project version name and SemVer to V3

## Tasks
- [x] Update version to `3.0.0` and references of `V2`/`v2` to `V3`/`v3` in `AGENTS.md`, `README.md`, and `.agents/rules.md` <!-- id: task-docs-version -->
- [x] Update version and references in `bootstrap.sh`, `bootstrap.ps1`, `install.sh`, and `install.ps1` <!-- id: task-installers-version -->
- [x] Update version and references in core scripts and CLI helpers under `.agents/scripts/` <!-- id: task-scripts-version -->
- [x] Run validate to verify all checks and unit tests pass successfully <!-- id: task-validation -->

## Acceptance Criteria
- [x] All instances of "AAC V2" or "Antigravity V2" in documentation and bootstrap messages are updated to "V3"
- [x] SemVer version is bumped to `3.0.0` in AGENTS.md, README.md, and installer scripts
- [x] All 192 unit tests pass successfully

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] AGENTS.md <!-- id: target-agents -->
  - [x] README.md <!-- id: target-readme -->
  - [x] .agents/rules.md <!-- id: target-rules -->
  - [x] bootstrap.sh <!-- id: target-boot-sh -->
  - [x] bootstrap.ps1 <!-- id: target-boot-ps1 -->
  - [x] install.sh <!-- id: target-inst-sh -->
  - [x] install.ps1 <!-- id: target-inst-ps1 -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: target-boot-py -->
- Active module locks:
  - [ ] bootstrap <!-- id: lock-bootstrap -->
  - [ ] dashboard <!-- id: lock-dashboard -->
  - [ ] learn <!-- id: lock-learn -->
  - [ ] upgrade <!-- id: lock-upgrade -->
  - [ ] validate <!-- id: lock-validate -->
  - [ ] run_benchmarks <!-- id: lock-run_benchmarks -->
  - [ ] sync <!-- id: lock-sync -->
  - [ ] helper <!-- id: lock-helper -->
  - [ ] mcp <!-- id: lock-mcp -->
  - [ ] .agents/scripts/cli/__init__ <!-- id: lock-__init__ -->
  - [ ] .agents/scripts/cli/commands/__init__ <!-- id: lock-__init__ -->
  - [ ] .agents/scripts/mcp_server <!-- id: lock-mcp_server -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
