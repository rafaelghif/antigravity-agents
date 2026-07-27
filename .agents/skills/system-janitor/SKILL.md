---
name: system-janitor
description: Token budget optimizer, context memory compactor, process manager, and incident recovery specialist. Triggers when context usage exceeds budget, cleaning intermediate scratch files, or handling execution timeouts.
requires_core: ">=4.2.0"
---
# System Janitor Skill

## Objective
Manage context token budgets, purge ephemeral scratch files, and oversee process execution timeouts.

## 1. Token Budget & Memory Compaction
- Monitor token usage metrics (`state.json -> token_usage`).
- When `current_used` reaches $> 80\%$ of `max_budget` (100,000 tokens), compact memory notes into `.agents/scratch/compaction.md`.
- Purge intermediate scratch files upon task completion to keep context baseline ultra-lean.

## 2. Ephemeral Process & Incident Recovery
- Manage background process execution timeouts (`config.json -> timeouts.abort_minutes`).
- Generate post-mortem incident reports under `.agents/incidents/` if execution encounters deadlocks or safe aborts.
