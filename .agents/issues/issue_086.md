---
id: issue-086
title: "Implement Auto-Configuration GPG Signing when Switching Profiles"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Implement Auto-Configuration GPG Signing when Switching Profiles

## Tasks
- [x] Task 1: Create Pre-Implementation Impact Analysis and option decisions.
- [x] Task 2: Implement configure_git_signing helper and integrate into switch_profile in profile.py.
- [x] Task 3: Update unit tests in test_profile.py to assert git configs are set/unset correctly.
- [x] Task 4: Verify full test suite and validation checks pass.

## Acceptance Criteria
- [x] Switching to a profile with gpg_key_id sets local user.signingkey and commit.gpgsign = true.
- [x] Switching to a profile without gpg_key_id unsets user.signingkey and sets commit.gpgsign = false.
- [x] All unit and integration tests pass successfully.
