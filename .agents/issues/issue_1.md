---
id: issue-1
title: "Optimize core agent prompt and enforce Hermes protocol"
status: open
assignee: agent-antigravity
milestone: "v3.127"
created_at: 2026-07-17
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Markdown
- **Architecture**: Core prompt optimization
- **Key Modules**: `AGENTS.md`, `.agents/skills/task-management/SKILL.md`, `.agents/templates/AGENTS.md.template`

## Tasks
- [x] Compress AGENTS.md for token optimization <!-- id: task-1 -->
- [x] Enforce Epic-Task branching in AGENTS.md and task-management SKILL <!-- id: task-2 -->
- [x] Inject Hermes Protocol into AGENTS.md <!-- id: task-3 -->
- [ ] Sync AGENTS.md to .agents/templates/AGENTS.md.template <!-- id: task-4 -->
- [ ] Commit changes on proper branch and merge <!-- id: task-5 -->
- [ ] Record mistake in lessons-learned.md <!-- id: task-6 -->

## Acceptance Criteria
- [x] Pre-commit hook passes <!-- id: ac-1 -->

## Rule & Schema Compliance Audit
- [x] No schema changes required <!-- id: audit-1 -->
