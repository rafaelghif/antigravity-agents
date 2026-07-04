---
id: issue-151
title: "Enhance and harden bootstrapper, dashboard, and validation interactivity"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Enhance and harden bootstrapper, dashboard, and validation interactivity

## Tasks
- [x] Harden validation script to respect non-interactive environment flags and avoid hangs
- [x] Allow host, port, and external access overrides in dashboard HTTP server configuration
- [x] Add --update/--force flags to bootstrapper to support file updates
- [x] Implement and verify unit tests for all updates

## Acceptance Criteria
- [x] Validation does not prompt for user input when ANTIGRAVITY_NONINTERACTIVE, ANTIGRAVITY_AGENT, or CI are set
- [x] Dashboard supports --host, --port, and --allow-external arguments and binds accordingly
- [x] Bootstrapper overwrites existing files if --update or --force is specified
- [x] All unit tests pass successfully
