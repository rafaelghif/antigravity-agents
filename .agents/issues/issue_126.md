---
id: issue-126
title: "Optimize prompt token footprint, prevent duplicate self-learning rules, and prune redundant CLI context"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Optimize prompt token footprint, prevent duplicate self-learning rules, and prune redundant CLI context

## Tasks
- [x] Task 1: Prevent duplicate lessons from being appended to lessons-learned.md in learn.py
- [x] Task 2: Deduplicate synthesized rules in rules.md when syncing in sync.py
- [x] Task 3: Shorten custom skills loading behavior text in sync.py to optimize AGENTS.md footprint
- [x] Task 4: Instruct agents to read optimized context file in AGENTS.md working protocol
- [x] Task 5: Verify and run validation tests

## Acceptance Criteria
- [x] lessons-learned.md contains no duplicate lesson lines
- [x] rules.md has unique rules in Section 5 (Self-Learning Memory)
- [x] AGENTS.md custom skills table uses short 'On match' status for loading behavior
- [x] AGENTS.md includes instruction to read active_context.md at the start of tasks
- [x] Local tests pass successfully
