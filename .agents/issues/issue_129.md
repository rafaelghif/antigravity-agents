---
id: issue-129
title: "Fix visual status dashboard UI/UX loading bug, threading HTTP server bottleneck, and terminal stdout clutter"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Fix visual status dashboard UI/UX loading bug, threading HTTP server bottleneck, and terminal stdout clutter

## Tasks
- [x] Task 1: Update dashboard imports, add thread-safety lock and ThreadingHTTPServer in dashboard.py
- [x] Task 2: Implement run_silent_validation and background initial audit worker thread to cache compliance status
- [x] Task 3: Handle URL query parameters in do_GET and support force=true parameter for on-demand audits
- [x] Task 4: Fix switchTab JavaScript browser compatibility bug (passing 'this' element) and add interactive loading state

## Acceptance Criteria
- [x] Dashboard is non-blocking, multi-threaded, and loads instantly without hanging
- [x] Visual dashboard audits do not clutter or print validation logs to the terminal
- [x] Click on Refresh button triggers silent synchronous audit and re-enables properly
- [x] Tab switching works correctly on all modern browsers without ReferenceErrors
