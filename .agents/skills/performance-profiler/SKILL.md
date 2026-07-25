---
name: performance-profiler
description: Profile code for performance regressions
instruction: Use on critical paths or when modifying complex algorithms to ensure no performance degradation occurs.
requires_core: ">=4.0.0"
---
# Performance Profiler Skill

## Objective
Identify and resolve performance bottlenecks such as N+1 queries, memory leaks, and inefficient algorithms.

## When to Execute
- When modifying database queries or loops processing large datasets.
- During PR reviews for performance-critical modules.

## Execution Steps
1. Check for N+1 queries in ORM/database operations.
2. Analyze loops for inefficient algorithmic complexity (e.g., O(n²) vs O(n)).
3. Check for memory leaks. Run memory profiler in production mode for 5 minutes with simulated load. Track heap size growth pattern: if +10% in <5 minutes → investigate. Check event listener count: `process._getActiveHandles()` (Node.js) or `len(weakref.getweakrefs())` (Python). Report findings with before/after heap snapshots.
4. For frontend applications, run Lighthouse (or similar) to evaluate performance metrics.
5. Report findings in `.agents/plans/perf-<date>.md` and propose optimizations.
