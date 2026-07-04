---
id: 182
title: "Optimize token sync to run asynchronously in background"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Calling `sync_from_platform_usage` synchronously during token logging blocks the CLI/pre-commit execution for 3-5 seconds because of fallback invocation of `agy -p "/usage"`. This creates visible latency for the developer.

## Pre-Implementation Impact Analysis

### Option A: Asynchronous Detached Subprocess (Recommended)
- **Implementation**: In `run_log` after token logs are saved, spawn `./helper.sh token sync --auto` as a detached subprocess in the background (`subprocess.Popen` with `start_new_session=True` / `CREATE_NEW_PROCESS_GROUP`).
- **Pros**: `token log` returns instantly (< 50ms). Zero wait time for the user. Highly robust.
- **Cons**: Limits won't reload immediately in the foreground run (warnings might use previous synced limit, which is acceptable).

### Option B: Synchronous Parsing Optimization
- **Implementation**: Attempt to speed up `agy -p "/usage"` itself.
- **Cons**: Impossible because `agy` is a separate agent-based tool whose boot/initialization time is controlled by the platform.

### Recommendation
**Option A** is the best path forward to achieve high-performance and zero-lag user experience.

---

## Tasks
- [x] Refactor `run_log` in [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py) to spawn the token sync command asynchronously.
- [x] Run validation suite to confirm compliance.

## Acceptance Criteria
- [x] `./helper.sh token log <p> <c>` returns instantly (< 100ms) without blocking.
- [x] The background sync process executes successfully and updates local token budget.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/token.py <!-- id: audit-target-files -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/token <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
