---
id: issue-193
title: "Fix installer memory leak and identity separation for target projects"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The installer copies active `AGENTS.md` and `.agents/rules.md` directly from the main agent repository to the target project. This pollutes target project workspaces with the Python/PEP-8 requirements and CLI-specific synthesized rules (Self-Learning memory) of the CLI tool repository. Because the product remains `test-proj`, the agent in target projects thinks it is the CLI repository, causing a severe identity crisis and hallucinated code generation instead of asking questions.

## Tasks
- [x] Add non-negotiable rule in `AGENTS.md` requiring interactive requirement gathering (specs, database, environment, framework/libraries) before feature development. <!-- id: subtask-agents-rule -->
- [x] Create `.agents/templates/rules.md.template` as a clean stack-agnostic template for target projects. <!-- id: subtask-rules-template -->
- [x] Update `bootstrap.py` to exclude `rules.md` from standard helpers and dynamically generate it from the new template. <!-- id: subtask-bootstrap-py -->
- [x] Update `install.sh` and `install.ps1` to exclude `.agents/rules.md` from the copy logic. <!-- id: subtask-install-scripts -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] `AGENTS.md` contains the new rule prohibiting hallucinations and requiring explicit questioning.
- [x] Target projects bootstrapped with a different stack (e.g. Node, PHP) get a clean `.agents/rules.md` without CLI-specific rules or Python code rules.
- [x] All installer scripts and python unit tests run successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/scripts/cli/commands/bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py)
  - [install.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.sh)
  - [install.ps1](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.ps1)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-193`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
