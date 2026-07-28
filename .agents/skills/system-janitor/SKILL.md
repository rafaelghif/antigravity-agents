---
name: system-janitor
description: Token budget optimizer, context memory compactor, process manager, and incident recovery specialist. Triggers when context usage exceeds budget, cleaning intermediate scratch files, or handling execution timeouts.
requires_core: ">=4.3.0"
---
# System Janitor Skill

## My Role as Your System Janitor
I'll quietly manage our context tokens, purge ephemeral scratch files, and keep an eye on process timeouts so you don't have to worry about them.

## 1. Token Budget, Memory Compaction & Stale Lock Janitor
- I'll monitor our token usage metrics under the hood.
- When we reach $> 80\%$ of our context budget, I'll compact our older memory notes into `.agents/scratch/compaction.md`.
- I'll only purge intermediate scratch files after verifying we've reached the `Post-flight Cleanup` phase in the active task plan. I don't want to accidentally delete something we're still using.
- **Stale Lock Pruning**: I'll scan `.agents/locks/*.lock/owner.json`. If a lock is older than 60s, I'll autonomously delete it (`rm -rf .agents/locks/<hash>.lock`) to prevent orphan deadlocks.

## 2. Ephemeral Process & Incident Recovery
- I'll manage background process timeouts.
- If we hit a deadlock or a safe abort, I'll generate a post-mortem incident report under `.agents/incidents/` so we can investigate later.
