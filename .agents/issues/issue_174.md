---
id: issue-174
title: "Implement token usage trend and remaining reset time displays"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Implement token usage trend and remaining reset time displays

## Tasks
- [x] Add reset remaining time calculation to token.py and status command
- [x] Parse log file for token trend in dashboard.py status API
- [x] Add HTML widgets for remaining resets and sparkline chart in index.html
- [x] Implement UI rendering for sparkline and resets in app.js
- [x] Add tests for reset times in test_token.py
- [x] Run validation checks and verify they pass

## Acceptance Criteria
- [x] CLI status displays remaining time for 5-hour, Daily, Weekly, and Monthly resets
- [x] Dashboard displays remaining reset times and a visual sparkline/trend chart of token usage
- [x] validate.py passes successfully
