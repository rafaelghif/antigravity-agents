---
id: issue-216
title: "Implement remaining audit fixes: install checks, passphraseless SSH, markdown relative link audit"
status: open
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement remaining audit fixes: install checks, passphraseless SSH, markdown relative link audit

## Tasks
- [x] Add python version checks and environment variable source repo support in install.sh and install.ps1 <!-- id: task-install-checks -->
- [x] Add env repo override support in upgrade.py and bootstrap.py <!-- id: task-repo-overrides -->
- [x] Ask developer for passphrase confirmation or default to secure passphraseless SSH key generation in profile.py <!-- id: task-ssh-passphrase -->
- [x] Extend validate.py link checks to audit standard relative markdown links <!-- id: task-link-audit -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] install.sh and install.ps1 verify Python >= 3.8 and support AAC_SOURCE_REPO.
- [x] upgrade.py and bootstrap.py support repository source override environment variables.
- [x] profile.py warns about passphraseless SSH key creation or prompts for interactive input.
- [x] validate.py correctly audits standard markdown relative path links and relative anchor ranges.
- [x] The entire workspace passes validation checks.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [install.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.sh)
  - [install.ps1](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.ps1)
  - [.agents/scripts/cli/commands/upgrade.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/upgrade.py)
  - [.agents/scripts/cli/commands/bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py)
  - [.agents/scripts/cli/commands/profile.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/profile.py)
  - [.agents/scripts/validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py)
- Active module locks:
  - `profile`, `upgrade`, `bootstrap`, `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
