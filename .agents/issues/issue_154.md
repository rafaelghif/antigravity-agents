---
id: issue-154
title: "Explicitly restrict git configuration to local workspace level"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Explicitly restrict git configuration to local workspace level

## Tasks
- [x] Restrict Git config calls in bootstrap.py to explicitly use --local flag

## Acceptance Criteria
- [x] Onboarding profile configuration sets user.name and user.email with --local parameter
