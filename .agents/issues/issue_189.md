---
id: issue-189
title: "Enforce issue schemas and implement atomic file writing"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Enforce issue schemas and implement atomic file writing

## Tasks
- [x] Remove duplicate git hook templates from bootstrap scripts and run validate.py instead <!-- id: task-bootstrap-hooks -->
- [x] Implement atomic file writing using tempfile and os.replace in lock.py and token.py <!-- id: task-atomic-writing -->
- [x] Update unit tests for lock.py to verify NamedTemporaryFile atomic mock calls <!-- id: task-test-lock -->
- [x] Implement audit_issue_files_schema to validate markdown frontmatter and headers <!-- id: task-issue-schema -->

## Acceptance Criteria
- [x] No duplicate inline hook templates exist in bootstrap.sh/bootstrap.ps1.
- [x] lock.py and token.py save configuration files atomically.
- [x] All issue specification files under .agents/issues/ have their YAML frontmatter and section layout validated.
