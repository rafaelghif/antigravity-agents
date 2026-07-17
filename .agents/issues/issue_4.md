---
id: issue-4
title: "Fix target project installation data leaks"
status: open
assignee: agent-antigravity
milestone: "v3.129"
created_at: 2026-07-17
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python, Markdown
- **Architecture**: Core CLI Installation

## Tasks
- [x] Analyze bootstrap.py and templates for data leaks <!-- id: task-1 -->
- [x] Restore {{PRODUCT}}, {{VERSION}}, and {{STACK}} placeholders in AGENTS.md.template <!-- id: task-2 -->
- [x] Add logic to copy git_profiles.example to git_profiles.json in bootstrap.py <!-- id: task-3 -->
- [ ] Run helper.sh changelog and commit <!-- id: task-4 -->

## Acceptance Criteria
- [ ] New projects generate clean metadata without test-proj leaks <!-- id: ac-1 -->
- [ ] git_profiles.json is generated correctly <!-- id: ac-2 -->

## Rule & Schema Compliance Audit
- [x] Code strictly follows target isolation <!-- id: audit-1 -->
