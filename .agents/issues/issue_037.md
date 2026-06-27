---
id: issue-037
title: "Validate GPG signing key validity during profile switch"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
When a developer switches profiles, and the profile contains a `signing_key` for GPG-signed commits, we currently configure Git locally without checking if the GPG key is installed on the developer's system. This can lead to Git commit failures later. We need to validate the key using local `gpg --list-secret-keys` before applying it, unless overridden by `--force-no-gpg`.

## Tasks
- [x] Implement GPG key validation using `gpg --list-secret-keys` in profile.py
- [x] Implement `--force-no-gpg` override option in profile.py
- [x] Add unit tests for GPG validation success, failure, and override scenarios in test_profile.py
- [x] Validate and close issue-037 using the automated close command

## Acceptance Criteria
- [x] Switching to a profile with a missing/invalid GPG key fails and prompts warning, aborting the switch
- [x] Using `--force-no-gpg` successfully switches the profile even if the GPG key check fails
- [x] All unit tests pass successfully
