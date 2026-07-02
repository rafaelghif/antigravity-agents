---
name: performance-optimization
description: Guidelines for CPU profiling, identifying database query bottlenecks (N+1 queries), diagnosing memory leaks, and optimizing resource execution speeds.
---

# Performance Profiling & Optimization Playbook

This playbook establishes the engineering rules for diagnosing performance bottlenecks, profiling memory allocations, and optimizing execution runtimes.

---

## 1. Relational Database Query Profiling

Slow database queries are the primary cause of latency in enterprise applications.

### A. The N+1 Query Problem
- **Identify**: An N+1 query happens when an application executes 1 initial query to fetch a list of parent records, followed by N separate queries to fetch related child records for each parent.
- **Resolve**: Always use eager loading (relationships joining or fetching in bulk) to reduce database round-trips:
  - Django/Python: use `select_related()` (for ForeignKey/OneToOne) or `prefetch_related()` (for ManyToMany).
  - Laravel/Eloquent: use `with(['relationship_name'])`.
  - Node/ORM: use eager fetching joins.

### B. Index Analysis with EXPLAIN ANALYZE
Before adding indexes, analyze query plans:
1. Prepend `EXPLAIN (ANALYZE, BUFFERS)` in PostgreSQL or `EXPLAIN` in MySQL to the query.
2. Search for:
   - **Seq Scan / Full Table Scan**: Indicates missing indexes.
   - **Filter**: Checks rows individually, which is slow on large datasets.
3. Optimize by creating appropriate composite or concurrent indexes.

---

## 2. Memory Diagnostics & Memory Leak Prevention

- **Diagnostics**:
  - Python: Use `tracemalloc` to track memory blocks or `memory_profiler` to inspect line-by-line allocations.
  - Node: Use `--inspect` and Chrome DevTools to capture Heap Snapshots.
- **Common Memory Leaks**:
  - **Global Variables**: Storing large maps or lists in module-level global variables.
  - **Uncleared Subscriptions / Listeners**: Missing cleanups in event-driven frameworks.
  - **Open Stream Leaks**: Forgetting to close file handlers or database connections. Always wrap resources in context managers.

---

## 3. CPU Profiling & Execution Speed Optimization

- **Profiling Tools**:
  - Python: Use `cProfile` and generate visual call graphs via `gprof2dot` or `snakeviz`.
  - Node: Use `clinic.js` or built-in `--prof` profile analysis.
- **Optimization Strategy**:
  - **Avoid Nested Loops**: Refactor $O(N^2)$ nested loops into $O(N)$ operations by using dictionaries (hash maps) or sets.
  - **Lazy Initialization**: Postpone heavy operations (like reading files, parsing JSON, or connecting to services) until they are actually needed.
  - **Asynchronous Execution**: Offload long-running tasks to background queues (Celery, BullMQ) rather than blocking the main HTTP thread.
