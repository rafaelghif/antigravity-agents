---
id: 330
title: "fix: harden core and verify installation manifest"
status: closed
assignee: rafaelghif
created_at: 2026-07-12
github_url: "https://github.com/rafaelghif/antigravity-agents/issues/29"
github_number: 29
---

# Issue Details

## Problem Statement
fix: harden core and verify installation manifest

## Tasks
- [x] Exclude wrapper/installer/dev files (`bootstrap.sh`, `bootstrap.ps1`, `install.sh`, `install.ps1`, `requirements.txt`, `pyproject.toml`, `.github` folder) from copying in `install.py`. <!-- id: task-exclude-installer-files -->
- [x] Customize target project `AGENTS.md` and `.agents/rules.md` in `bootstrap.py` when `is_core` is False. <!-- id: task-customize-target-agents-rules -->
- [x] Disable core-only validation checks (bootstrap.py version check, here-doc script audit, locks/budget raw write audit) in `validate.py` when `is_core` is False. <!-- id: task-disable-core-validation-checks -->

## Acceptance Criteria
- [x] Installation to target project does not copy `bootstrap.sh/ps1`, `install.sh/ps1`, `requirements.txt`, `pyproject.toml`, or `.github`.
- [x] Target project `AGENTS.md` has generic repo layout and no installer/bootstrap sync rule.
- [x] Target project `.agents/rules.md` has no template/wrapper parity rule.
- [x] Validation guard checks for target projects bypass core-specific version and compliance checks.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/cli/commands/install.py` <!-- id: audit-install-py -->
  - [x] `.agents/scripts/cli/commands/bootstrap.py` <!-- id: audit-bootstrap-py -->
  - [x] `.agents/scripts/validate.py` <!-- id: audit-validate-py -->
- Active module locks:
  - [x] `.agents/scripts/cli/commands/install.py` <!-- id: lock-install -->
  - [x] `.agents/scripts/cli/commands/bootstrap.py` <!-- id: lock-bootstrap -->
  - [x] `.agents/scripts/validate.py` <!-- id: lock-validate -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
