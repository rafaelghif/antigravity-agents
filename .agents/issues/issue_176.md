---
id: issue-176
title: "Integrate agy usage command extraction"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Integrate agy usage command extraction

## Tasks
- [x] Programmatically extract real token usage statistics from agy TUI/CLI
- [x] Parse extracted metrics and update token_budget.json dynamically
- [x] Update CLI status and dashboard to display the real extracted data
- [x] Add tests for automated usage extraction
- [x] Run validation checks and verify they pass

## Acceptance Criteria
- [x] running token status updates database with actual metrics fetched from agy TUI/CLI
- [x] Dashboard shows the exact real usage and reset countdowns in real-time
- [x] validate.py passes successfully
