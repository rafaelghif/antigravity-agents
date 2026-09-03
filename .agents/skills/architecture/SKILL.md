---
name: architecture
description: Use this skill for system design, distributed architecture, strict RFC 7807 API contracts, and resilience engineering (idempotency, outbox, circuit breaker).
---

# Enterprise Architecture & Distributed Systems Protocol

<CRITICAL_DIRECTIVE>
Execute Principal Architect procedural rigor. Enforce clear domain boundaries, strict backward-compatible API contracts, and fault-tolerant distributed resilience.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Architectural Style & DDD**:
   - Strictly conform to project's established style (Clean Architecture, Hexagonal, MVC, or Modular).
   - Domain isolation: separate controllers, domain business logic, and repository data layers.
   - Boring and minimal beats clever and bloated (YAGNI). Speculative generic wrappers are forbidden.
2. **API Contract Governance & Backward Compatibility**:
   - APIs are permanent public contracts. Field deletion or renaming is BANNED without major version bumps.
   - Enums are append-only. New request fields MUST be optional with sensible defaults.
   - Standardized RFC 7807 Problem Details: All HTTP error responses must return structured JSON (`type`, `title`, `status`, `detail`, `code`). Never leak raw stack traces.
   - Schema-First Validation: Validate all input payloads through strict DTO schemas (Zod, Pydantic, Protobuf).
3. **Distributed Resilience & Fault Tolerance**:
   - **Idempotency Keys**: All state-mutating endpoints (payments, order placement, credits) require an `Idempotency-Key` header with cached response re-delivery.
   - **Full Jitter Exponential Backoff**: Never use fixed sleep. Apply randomized exponential backoff:
     $$T_{\text{sleep}} = \text{random}(0, \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}))$$
   - **Transactional Outbox Pattern**: Never write to DB and message broker directly. Write events to an `outbox` table in the same DB transaction; dispatch via dedicated CDC/worker.
   - **Circuit Breakers**: Wrap external network calls in circuit breakers (trip open on >50% failure window; serve graceful cached/queued fallbacks).
   - **Deadlock Prevention**: Acquire locks in globally sorted order (by entity ID/UUID). Prefer optimistic version locking.
4. **Database Performance & Anti-N+1**:
   - Mandate index utilization for frequent queries. Prevent N+1 query patterns in ORMs via eager loading/joins.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Discovery & Blast Radius**: Trace affected components using `grep_search` or `scripts/semantic_grapher.py`.
2. **Contract & Resilience Design**: Define backward-compatible schema, DTO validation, idempotency, and error handling.
3. **Verify Under Chaos**: Ensure circuit breakers, retries, and outbox tables handle network timeouts and concurrency.
4. **Approval**: Provide an Architecture Decision Record (ADR) detailing blast radius before executing breaking refactors.
</PROCEDURAL_WORKFLOW>
