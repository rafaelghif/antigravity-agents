---
name: system-janitor
description: Token budget optimizer, context memory compactor, process manager, and incident recovery specialist. Triggers when context usage exceeds budget, cleaning intermediate scratch files, or handling execution timeouts.
requires_core: ">=4.3.0"
---
# System Janitor Skill

## Objective
Manage context token budgets, purge ephemeral scratch files, and oversee process execution timeouts.

## 1. Token Budget, Memory Compaction & Stale Lock Janitor
- Monitor token usage metrics via `audit.jsonl` logs or internal payload.
- When token consumption reaches $> 80\%$ of budget, compact memory notes into `.agents/scratch/compaction.md`.
- Purge intermediate scratch files ONLY after verifying the main agent has reached the `Post-flight Cleanup` phase in the active task plan, to prevent cleanup race conditions.
- **Stale Lock Pruning Protocol**: Scan `.agents/locks/*.lock/owner.json`. If `claimed_at` timestamp is older than `config.json -> state_management.lock_timeout_seconds` (60s), autonomously delete the stale lock directory (`rm -rf .agents/locks/<hash>.lock`) to prevent orphan deadlocks.



## 2. Ephemeral Process & Incident Recovery
- Manage background process execution timeouts (`config.json -> timeouts.abort_minutes`).
- Generate post-mortem incident reports under `.agents/incidents/` if execution encounters deadlocks or safe aborts.
