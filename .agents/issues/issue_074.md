---
id: issue-074
title: "Implement Git HTTPS Credentials Rotation Integration"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Implement Git HTTPS Credentials Rotation Integration

## Tasks
- [x] Task 1: Add git_token property to git_profiles configurations.
- [x] Task 2: Implement credential-helper subcommand and Git config injection logic.
- [x] Task 3: Implement comprehensive unit tests.

## Acceptance Criteria
- [x] profile subcommand credential-helper prints username and password on get command.
- [x] credential-helper configuration is unstageable, and git local config updates automatically on profile switch.
