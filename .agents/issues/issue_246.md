---
id: issue-246
title: "feat: zero-config bootstrap, pause/resume agent hand-off, and safe agent commands"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Implement additional developer experience (DX) and safety improvements:
1. Zero-config bootstrap option via `--quick` / `-q`.
2. Agent pause/resume hand-off mechanisms via `helper.sh pause` and `helper.sh resume`.
3. Quiet validation check styling via `-q` / `--quiet` to suppress status spam.
4. Restrict agent from executing destructive Git commands (added rules in AGENTS.md).

## Tasks
- [x] Implement `--quick` / `-q` setup auto-detection in `bootstrap.py`. <!-- id: task-bootstrap-quick -->
- [x] Create `pause.py` and `resume.py` command files. <!-- id: task-pause-resume -->
- [x] Filter out validation spam in `validate.py` when quiet mode is active. <!-- id: task-validate-quiet -->
- [x] Restrict agent Git commands by adding strict non-destructive rule to `AGENTS.md`. <!-- id: task-agent-git-restriction -->

## Acceptance Criteria
- [x] `./helper.sh bootstrap -q` runs instantly using auto-detected values. <!-- id: criteria-bootstrap-quick -->
- [x] `./helper.sh pause` blocks any further agent tool execution; `./helper.sh resume` reactivates it. <!-- id: criteria-pause-resume -->
- [x] `./helper.sh validate -q` runs silently and only shows errors. <!-- id: criteria-validate-quiet -->
- [x] Agent is strictly forbidden from running destructive Git commands via non-negotiables in AGENTS.md. <!-- id: criteria-agent-git-restriction -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/cli/commands/bootstrap.py`
  - [x] `.agents/scripts/cli/helper.py`
  - [x] `AGENTS.md`
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/helper <!-- id: lock-helper -->
  - [x] .agents/scripts/cli/commands/pause <!-- id: lock-pause -->
  - [x] .agents/scripts/cli/commands/resume <!-- id: lock-resume -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
