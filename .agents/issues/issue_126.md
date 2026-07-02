---
id: issue-126
title: "Optimize prompt token footprint, prevent duplicate self-learning rules, and prune redundant CLI context"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Optimize prompt token footprint, prevent duplicate self-learning rules, and prune redundant CLI context

## Tasks
- [ ] Task 1: Prevent duplicate lessons from being appended to lessons-learned.md in learn.py
- [ ] Task 2: Deduplicate synthesized rules in rules.md when syncing in sync.py
- [ ] Task 3: Shorten custom skills loading behavior text in sync.py to optimize AGENTS.md footprint
- [ ] Task 4: Instruct agents to read optimized context file in AGENTS.md working protocol
- [ ] Task 5: Verify and run validation tests

## Acceptance Criteria
- [ ] lessons-learned.md contains no duplicate lesson lines
- [ ] rules.md has unique rules in Section 5 (Self-Learning Memory)
- [ ] AGENTS.md custom skills table uses short 'On match' status for loading behavior
- [ ] AGENTS.md includes instruction to read active_context.md at the start of tasks
- [ ] Local tests pass successfully
