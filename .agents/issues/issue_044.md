---
id: issue-044
title: "Implement enterprise-grade Observability & Logging skill playbook"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Markdown Playbook
- **Architecture**: Introduce standard observability guidelines (structured logging, distributed tracing, metrics, error tracking) under `.agents/skills/observability/`.
- **Key Modules**:
  - [.agents/skills/observability/SKILL.md](file://./.agents/skills/observability/SKILL.md)
  - [AGENTS.md](file://./AGENTS.md)
  - [README.md](file://./README.md)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Create `.agents/skills/observability/SKILL.md` with structured logging, OpenTelemetry tracing, Prometheus metrics, and error handling guidelines <!-- id: subtask-create-skill -->
- [x] Register and index the new observability skill in `AGENTS.md` and `README.md` <!-- id: subtask-register-skill -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] The `observability` skill is registered and fully integrated
