---
id: issue-6
title: "Dynamic Generation of projects.json and git_profiles.json during bootstrap"
status: open
assignee: agent-antigravity
milestone: "v3.131"
created_at: 2026-07-17
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3
- **Architecture**: CLI Bootstrapper

## Tasks
- [x] Auto-scan root directory for multi-project workspaces (e.g. backend/frontend) in `bootstrap.py` <!-- id: task-1 -->
- [x] Dynamically generate `.agents/projects.json` mapping based on directory scan <!-- id: task-2 -->
- [x] Fetch `git config user.name` and `user.email` to generate `.agents/git_profiles.json` dynamically <!-- id: task-3 -->
- [ ] Push to main <!-- id: task-4 -->

## Acceptance Criteria
- [ ] Target projects reflect accurate multi-component layout upon initialization <!-- id: ac-1 -->
- [ ] Git profiles match user's local git configuration instead of hardcoded example <!-- id: ac-2 -->

## Rule & Schema Compliance Audit
- [x] Target workspace metadata avoids hallucinated file paths <!-- id: audit-1 -->
