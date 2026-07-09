---
id: issue-209
title: "Enforce proactive prompt looping and self-driving zero-touch subtask execution"
status: open
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to ensure the agent does not loop for checking linting, but instead loops its thoughts/prompts proactively. The agent must know what to do next in a self-driving, zero-touch manner.

## Tasks
- [x] Update `AGENTS.md` to replace lint-check lookahead loops with proactive self-driving prompting loops <!-- id: task-agents-rules -->
- [x] Update active `rules.md` and `rules.md.template` with the proactive prompt looping rules <!-- id: task-rules-md -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Agent is guided to proactively execute subtasks sequentially in a single turn/session without halting for user prompts.
- [x] All unit tests pass successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
- Active module locks:
  - None
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
