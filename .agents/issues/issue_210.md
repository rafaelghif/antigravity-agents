---
id: issue-210
title: "Upgrade AGENTS.md to enterprise-grade master prompt template and execute self-driving execution loop"
status: open
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to rewrite `AGENTS.md` to be an enterprise-grade system prompt, guiding the agent through a zero-touch, self-correcting prompt loop, and execute it by committing it cleanly.

## Tasks
- [x] Rewrite `AGENTS.md` as an enterprise-grade system prompt template <!-- id: task-agents-rewrite -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] `AGENTS.md` is formatted cleanly with authoritative rules.
- [x] Zero-touch loop execution is documented and practiced.
- [x] Validation suite passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
- Active module locks:
  - None
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
