---
id: issue-217
title: "Implement Self-Evolving Agent Skills and optimize rules context"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement Self-Evolving Agent Skills and optimize rules context

## Tasks
- [x] Create dynamic skill evolution playbook under .agents/skills/skill-evolution/SKILL.md <!-- id: task-skill-evolution -->
- [x] Consolidate rules and prune duplicates in AGENTS.md and .agents/rules.md <!-- id: task-rules-prune -->
- [x] Run sync and validate tool to index the new skill <!-- id: task-sync-skills -->
- [x] Verify validation suite passes cleanly <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] A new specialized skill 'skill-evolution' is created and registered.
- [x] AGENTS.md and rules.md token footprint is reduced by consolidating redundant guidelines.
- [x] The entire validation checks suite passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/skills/skill-evolution/SKILL.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/skills/skill-evolution/SKILL.md)
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
- Active module locks:
  - `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
