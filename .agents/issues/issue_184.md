---
id: 184
title: "Optimize token sync reliability and freshness guards"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The token tracker has two major sync/validity issues:
1. `scan_conversations_for_usage` scans binary SQLite `.db` steps without age validation, potentially loading stale (e.g. 3-day-old) `/usage` outputs and blocking fresh platform fallback syncs.
2. Even when exact rolling limits are parsed from Markdown tables, `sync_from_platform_usage` overwrites them with calculations from `local_weekly` which is incomplete.
3. `run_status` doesn't automatically trigger syncs when the budget is stale.

## Pre-Implementation Impact Analysis

### Option A: Complete Sync & Freshness Overhaul (Recommended)
- **Implementation**:
  - Scan `transcript.jsonl` files (clean JSON) first in `scan_conversations_for_usage` and enforce a strict 5-minute age validation.
  - Avoid overwriting `weekly_limit` and `five_hour_limit` in `sync_from_platform_usage` if they are parsed directly from the table.
  - Store and load `weekly_used_override` and `five_hour_used_override` in the budget to prevent rounding errors.
  - Automatically check budget staleness (2 minutes age) in `run_status` and trigger background sync or db scan.
- **Pros**: Dynamic, accurate, non-blocking, completely solves all sync and validity failures.
- **Cons**: None.

---

## Tasks
- [x] Implement `trigger_background_sync` helper to unify background process spawning.
- [x] Update `scan_conversations_for_usage` to scan `transcript.jsonl` first and enforce 5-minute age validation for both transcript and DB steps.
- [x] Refactor `sync_from_platform_usage` to preserve exact parsed limits and save direct used overrides.
- [x] Update `get_rolling_stats` to use `weekly_used_override` and `five_hour_used_override`.
- [x] Refactor `run_status` to check staleness and synchronously scan or asynchronously trigger background sync.
- [x] Update unit tests in [test_token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_token.py).
- [x] Run validation suite to confirm compliance.

## Acceptance Criteria
- [x] `token status` displays correct platform rolling limits and used counts without rounding/calculation errors.
- [x] Stale database steps are skipped, and the fallback sync triggers automatically to fetch live platform data.
- [x] `token status` triggers syncs automatically when the budget is older than 2 minutes.

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
