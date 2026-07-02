---
id: issue-123
title: "Implement core design improvements: path-resolved module locks, environment token lookup, and interactive GPG/SSH auto-repair switch"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Implement core design improvements: path-resolved module locks, environment token lookup, and interactive GPG/SSH auto-repair switch

## Tasks
- [x] Task 1: implement relative path mapping and backward compatibility for module locks in validate.py
- [x] Task 2: Implement base branch check caching in validate.py to avoid redundant git calls
- [x] Task 3: Support env: prefix token extraction in git_api.py and profile.py
- [x] Task 4: Implement interactive missing GPG/SSH auto-repair switch in profile.py
- [x] Task 5: Mock base branch checks in unit tests in test_validate.py

## Acceptance Criteria
- [x] Module locks check uses path resolution to prevent collision on duplicate filenames
- [x] git show-ref calls are cached via module level cache
- [x] Tokens starting with env: are resolved via os.getenv
- [x] Switching profiles interactively prompts to generate SSH key or disable GPG sign locally
- [x] All 115 tests pass successfully
