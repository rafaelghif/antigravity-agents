---
id: issue-322
title: "Default installer bootstrap inputs and copy all missing memory files"
status: open
assignee: agent-antigravity
milestone: "v3.83.x"
created_at: 2026-07-12
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python
- **Architecture**: CLI Utility
- **Key Modules**: `.agents/scripts/cli/commands/bootstrap.py`, `.agents/scripts/cli/commands/install.py`

## Tasks
- [x] Update `bootstrap.py` to default empty inputs to `python` (stack) and `clean` (architecture) instead of exiting with an error. <!-- id: task-bootstrap-defaults -->
- [x] Add all core memory files (like `milestones.md`, `security-policy.md`, etc.) to the whitelisted `copy_if_missing_filenames` set in `install.py` to prevent missing files during setup. <!-- id: task-install-missing-copy -->
- [x] Verify test suite passes successfully. <!-- id: task-test-verify -->

## Acceptance Criteria
- [x] Installer setup completes successfully when all interactive prompts are skipped/left blank. <!-- id: crit-skip-defaults -->
- [x] All memory files (`milestones.md`, `security-policy.md`, etc.) are present in target directory after fresh installation. <!-- id: crit-all-files -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] [bootstrap.py](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/.agents/scripts/cli/commands/bootstrap.py) <!-- id: audit-bootstrap-files -->
  - [x] [install.py](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/.agents/scripts/cli/commands/install.py) <!-- id: audit-install-files -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
