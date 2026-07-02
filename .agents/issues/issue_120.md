---
id: issue-120
title: "Execute DX/UX enhancements, fallback lookups for archived tasks, and git performance optimizations"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Execute DX/UX enhancements, fallback lookups for archived tasks, and git performance optimizations

## Tasks
- [x] Refactor profile.py switch command GPG/SSH checks to warning warnings
- [x] Add .agents/archive/issues/ search fallbacks to changelog.py, issue.py, context.py, and validate.py
- [x] Optimize lock.py stale lock branch existence check to use a single Git show-ref call
- [x] Verify validations pass and close task

## Acceptance Criteria
- [x] Changing Git profiles with missing keys prints warnings instead of exiting with failure.
- [x] Running helper.sh changelog, validate, issue checkout, and context optimize works on archived issues.
- [x] running helper.sh lock uses a single Git call to check branches.
- [x] Local validation guard passes cleanly.
