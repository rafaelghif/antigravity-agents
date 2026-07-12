---
id: issue-323
title: "Enforce strict online Git protocols across installer, bootstrapper, and upgrader"
status: closed
assignee: agent-antigravity
milestone: "v3.84.x"
created_at: 2026-07-12
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Bash, PowerShell, Python
- **Key Modules**: `install.ps1`, `install.sh`, `bootstrap.py`, `upgrade.py`

## Tasks
- [x] Enforce online protocols (http/https/git/ssh) check in `install.ps1`. <!-- id: task-ps1-online -->
- [x] Enforce online protocols (http/https/git/ssh) check in `install.sh`. <!-- id: task-sh-online -->
- [x] Enforce online protocols (http/https/git/ssh) check in `bootstrap.py`. <!-- id: task-bootstrap-online -->
- [x] Enforce online protocols (http/https/git/ssh) check in `upgrade.py`. <!-- id: task-upgrade-online -->
- [x] Verify test suite passes successfully. <!-- id: task-test-verify -->

## Acceptance Criteria
- [x] All installation and upgrade operations fallback to the online git remote if a local path is detected. <!-- id: crit-online-only -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] [install.ps1](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/install.ps1) <!-- id: audit-ps1-files -->
  - [x] [install.sh](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/install.sh) <!-- id: audit-sh-files -->
  - [x] [bootstrap.py](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/.agents/scripts/cli/commands/bootstrap.py) <!-- id: audit-bootstrap-files -->
  - [x] [upgrade.py](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/.agents/scripts/cli/commands/upgrade.py) <!-- id: audit-upgrade-files -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/commands/upgrade <!-- id: lock-upgrade -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
