---
id: issue-147
title: "Inject Cache-Control headers in dashboard"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Inject Cache-Control headers in dashboard to prevent browser caching of JS/CSS and API endpoints.

## Tasks
- [x] Add Cache-Control headers to GET API handlers in dashboard.py
- [x] Add Cache-Control headers to serve_static_file handler in dashboard.py
- [x] Verification complete

## Acceptance Criteria
- [x] HTTP headers for API status and static files correctly include no-cache directives to ensure clean, real-time client loading
- [x] All unit tests and validation checks pass successfully
