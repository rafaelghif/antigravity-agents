---
id: issue-152
title: "Enforce Git source repository downloading for all installations, bootstrapping, and upgrades"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Enforce Git source repository downloading for all installations, bootstrapping, and upgrades

## Tasks
- [x] Enforce Git cloning of source templates at the start of bootstrapping in bootstrap.py
- [x] Remove local dev copy option and force Git download in install.sh and install.ps1
- [x] Implement and verify unit tests for Git-based bootstrapping and installations

## Acceptance Criteria
- [x] Bootstrapper fetches files from Git repository during execution
- [x] Installer scripts always perform network/Git-based retrieval instead of local copying
- [x] All unit tests pass successfully
