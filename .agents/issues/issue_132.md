---
id: issue-132
title: "Enhance dashboard security, scalability, and dynamic MIME type resolution for static files"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3 (standard libraries: `mimetypes`, `os`, `urllib`).
- **Architecture**: Secure path normalization and absolute prefix containment check to prevent directory traversal attacks. Dynamic mime-type discovery for static assets.
- **Key Modules**:
  - [.agents/scripts/cli/commands/dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/dashboard.py)
  - [.agents/tests/test_dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_dashboard.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Implement generic static file serving with absolute path validation (prefix check) and `mimetypes` lookup.
  - *Trade-off*: Maximizes security against directory traversal, and scales dynamically without modifications to Python code when frontend assets are added. Zero external dependencies.
- **Option B**: Continue with hardcoded file routing.
  - *Trade-off*: Very safe but completely non-scalable. Adding files (like images, fonts, sub-scripts) requires code edits.

## 2. Implementation Subtasks
- [ ] Subtask 1: Implement path-traversal guard, mimetypes initialization, and dynamic file serving in `dashboard.py`.
- [ ] Subtask 2: Add unit tests in `test_dashboard.py` to cover traversal blocking (403/404 responses), dynamic MIME type serving, and default index.html resolution.
- [ ] Subtask 3: Run validator checks and ensure all tests pass.

## 3. Acceptance Criteria
- [ ] Accessing `/`, `/index.html`, `/style.css`, and `/app.js` works successfully.
- [ ] Traversing out of the dashboard directory (e.g. `../../etc/passwd`) returns a `403 Forbidden` or `404 Not Found` response.
- [ ] Static files are served with the correct `Content-Type` header (e.g. `text/html`, `text/css`, `application/javascript`).
- [ ] Local validation guard and unittest suite pass without errors.
