---
id: issue-030
title: "Fallback to git local account when git_profiles.json is not configured"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
If `git_profiles.json` is not configured (or contains only placeholder profiles), the commit CLI command defaults to overwriting the local Git configuration with `corporate-work`. The validator also blocks commit operations due to email mismatch. We need to follow the git local account if configured, and only fallback to example profiles if no local account exists.

## Tasks
- [x] Implement local git config checks and placeholder bypass in commit.py
- [x] Implement placeholder bypass in validate.py git config email verification
- [x] Add unit tests covering local git config fallback scenarios
- [x] Validate and close issue-030 using the automated issue close command

## Acceptance Criteria
- [x] Commit command does not overwrite custom local Git config when profiles are unconfigured
- [x] Validator does not fail on email mismatch if profiles contain only placeholder examples
- [x] All unit tests pass
