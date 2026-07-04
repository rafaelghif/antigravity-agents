---
id: issue-191
title: "Enforce programmatic checks for AGENTS.md, rules.md, and schema.md"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Enforce programmatic checks for AGENTS.md, rules.md, and schema.md

## Tasks
- [x] Update `audit_link_integrity` to dynamically scan AGENTS.md, rules.md, schema.md, and all issues/memory files <!-- id: task-validate-links -->
- [x] Require `Rule & Schema Compliance Audit` section in `audit_issue_files_schema` validation <!-- id: task-validate-issue-schema-audit -->
- [x] Add Clean Architecture domain entity import constraints check using ast module in `audit_codebase_rules_compliance` <!-- id: task-validate-clean-arch -->
- [x] Update `issue_example.md` and all open issues to include the compliance audit section <!-- id: task-update-open-issues -->

## Acceptance Criteria
- [x] `./helper.sh validate` scans all workspace markdown files for link integrity.
- [x] `validate.py` requires all open issues to have the `Rule & Schema Compliance Audit` section.
- [x] `validate.py` blocks domain modules from importing non-standard/non-domain packages.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/issue.py <!-- id: audit-module-locks -->
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: audit-validate-lock -->
  - [x] .agents/scripts/cli/commands/issue <!-- id: audit-issue-lock -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
