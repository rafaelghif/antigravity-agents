---
id: issue-321
title: "Fix missing core files during installation"
status: closed
assignee: agent-antigravity
milestone: "v3.82.x"
created_at: 2026-07-12
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python
- **Architecture**: CLI Utility
- **Key Modules**: `.agents/scripts/cli/commands/install.py`

## Tasks
- [x] Add `copy_if_missing_filenames` set in `install.py` to allow copying critical files (like `rules.md`, `schema.md`, `AGENTS.md`) if they do not exist in target workspace. <!-- id: task-add-set -->
- [x] Modify copy loop in `install.py` to check for missing critical files. <!-- id: task-modify-loop -->
- [x] Validate installer copy behavior via tests. <!-- id: task-validate-installer -->

## Acceptance Criteria
- [x] Verification script passes all checks. <!-- id: crit-pass -->
- [x] Target directory receives critical files on fresh run. <!-- id: crit-target -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] [install.py](file:///D:/Muhammad%20Rafael%20Ghifari/Project/Agent/antigravity-agents/.agents/scripts/cli/commands/install.py) <!-- id: audit-target-files -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
