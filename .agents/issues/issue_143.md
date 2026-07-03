---
id: issue-143
title: "Consolidate and optimize rules to reduce token footprint"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Consolidate and optimize rules to reduce token footprint.

## Tasks
- [x] Implement rule clustering/combining and max threshold capping (archiving) in sync.py
- [x] Implement historical archive file at .agents/memory/lessons-archive.md
- [x] Update unit tests in test_sync.py to cover rule clustering and threshold limits
- [ ] Verification complete

## Acceptance Criteria
- [ ] Active rules in rules.md are capped at 5 and clustered to avoid duplicates
- [ ] Older/excess rules are archived to .agents/memory/lessons-archive.md
- [ ] All unit tests and validation checks pass cleanly
