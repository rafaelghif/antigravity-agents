---
id: issue-7
title: "Optimize Token Usage for Deep Workspace Initialization Scans"
status: open
assignee: agent-antigravity
milestone: "v3.132"
created_at: 2026-07-17
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Markdown / CLI Templates
- **Architecture**: Workflow Optimization

## Tasks
- [x] Modify `bootstrap.py` to rewrite the mandatory `task-init` instruction in `board.md` <!-- id: task-1 -->
- [x] Instruct main agent to delegate deep framework analysis (React, WPF, Next.js, etc.) to the `research` subagent <!-- id: task-2 -->
- [x] Update `AGENTS.md` Working Protocol with subagent delegation tip for initialization <!-- id: task-3 -->
- [ ] Commit and generate changelog <!-- id: task-4 -->

## Acceptance Criteria
- [ ] Main agent avoids token bloat during initialization by leveraging subagents for file scanning <!-- id: ac-1 -->
- [ ] Deep framework detection remains highly accurate through AI capability rather than brittle python logic <!-- id: ac-2 -->

## Rule & Schema Compliance Audit
- [x] Reduces context drift risk by keeping massive directory parsing off the main thread <!-- id: audit-1 -->
