---
id: swarm-orchestration
title: "feat: Swarm Orchestration Playbook for Subagents"
status: open
assignee: agent-antigravity
created_at: 2026-07-18
github_url: "https://github.com/rafaelghif/antigravity-agents/issues/69"
github_number: 69
---

# Issue Details

## Problem Statement
We need a robust playbook for Swarm Orchestration. The Parent Agent must be able to break down a large Epic, create sub-tasks locally in `.agents/issues/`, and autonomously spawn multiple subagents (using `invoke_subagent`). To prevent code conflicts, each subagent MUST be isolated in its own Git branch (Workspace: branch), and the Parent Agent will merge their PRs once completed.

## Tasks
- [x] Task 1: Create `.agents/skills/swarm-orchestration/SKILL.md` playbook structure <!-- id: task-1 -->
- [x] Task 2: Define instructions for Parent Agent task breakdown and `.agents/issues/` generation <!-- id: task-2 -->
- [x] Task 3: Define subagent spawning protocol using `Workspace: branch` and PR aggregation <!-- id: task-3 -->

## Acceptance Criteria
- [x] Playbook clearly instructs using isolated branches for subagents.
- [x] Strategy prevents code conflicts and requires Parent Agent to merge PRs.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] None <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
