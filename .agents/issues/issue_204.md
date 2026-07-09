---
id: issue-204
title: "Elevate token sync robustness and lock transaction safety to world class grade"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
AAC V2 requires elevated robustness to meet world-class enterprise-grade requirements:
1. Concurrency control over JSON files (`locks.json`, `token_budget.json`) is currently vulnerable to race conditions (read-modify-write).
2. The token platform sync parser (`parse_usage_output`) is highly dependent on fragile regex scrapers and should support structured formats (like JSON) as a first-class citizen.
3. Lock pruning inside `validate.py` does a raw open/write on `locks.json`, violating the atomic file writing rules.

## Tasks
- [x] Implement `FileLockMutex` class in [helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py) <!-- id: task-mutex-impl -->
- [x] Integrate `FileLockMutex` inside [lock.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/lock.py) <!-- id: task-lock-mutex -->
- [x] Integrate `FileLockMutex` inside [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py) and future-proof `parse_usage_output` with JSON support <!-- id: task-token-robustness -->
- [x] Upgrade [validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py) to write `locks.json` atomically in `prune_stale_locks()` <!-- id: task-validate-atomic -->
- [x] Add unit tests for the new `FileLockMutex` and JSON token parsing fallback <!-- id: task-unit-tests -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] All unit tests pass and test suite compiles cleanly.
- [x] Multiple concurrent processes attempting to read/write locks or token budgets are synchronized via `FileLockMutex`.
- [x] `parse_usage_output` successfully parses JSON token budget output if present.
- [x] `validate.py` has no raw writes to `locks.json`.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py)
  - [lock.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/lock.py)
  - [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py)
  - [validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py)
- Active module locks:
  - `lock`
  - `token`
  - `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
