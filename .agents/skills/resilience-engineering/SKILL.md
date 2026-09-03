---
name: resilience-engineering
description: >-
  Use this skill when designing or implementing distributed systems to enforce resiliency, idempotency keys, transactional outbox pattern, circuit breakers, and deadlock-free concurrency.
---

# Resilience Engineering Protocol

<CRITICAL_DIRECTIVE>
Distributed systems fail constantly. Never assume network calls, external APIs, or database writes succeed synchronously. Eliminate race conditions, duplicate executions, and cascading service outages.
</CRITICAL_DIRECTIVE>

<CORE_STANDARDS>
1. **Idempotency Keys**:
   - Every state-mutating endpoint (payments, order placement, credits, dispatch) MUST require an `Idempotency-Key` header or payload hash.
   - Cache and lock the idempotency key in DB/Redis with a status (`PROCESSING`, `COMPLETED`, `FAILED`) before executing work.
   - Return identical cached response on re-deliveries.

2. **Exponential Backoff with Full Jitter**:
   - Banned: Fixed sleep retries (`sleep(1)`).
   - Enforce exponential backoff with full randomized jitter:
     $$T_{\text{sleep}} = \text{random}(0, \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}))$$
   - Prevents "thundering herd" spikes against recovering downstream servers.

3. **Transactional Outbox Pattern**:
   - NEVER publish messages directly to Kafka/RabbitMQ/Redis inside an active database transaction.
   - Write events to an `outbox` table in the SAME transaction as entity mutations.
   - A dedicated poller/CDC worker consumes and dispatches outbox events reliably with at-least-once delivery.

4. **Circuit Breaker & Fallbacks**:
   - Wrap 3rd-party HTTP/gRPC clients in a Circuit Breaker (Closed -> Open -> Half-Open).
   - If downstream error rate exceeds 50% over a 10s window, trip open immediately and serve degraded graceful fallbacks (cached data, queued tasks) without waiting for timeouts.

5. **Concurrency & Deadlock Prevention**:
   - Always acquire locks on multiple resources in a deterministic, globally sorted order (e.g. sorted by UUID/ID).
   - Use optimistic locking with version integers (`WHERE id = :id AND version = :version`) over heavy table locks whenever possible.
</CORE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Identify Failure Domains**: Locate non-idempotent endpoints, network boundaries, and shared database locks.
2. **Implement Guardrails**: Apply idempotency checks, circuit breakers, and outbox tables.
3. **Verify Under Chaos**: Simulate network timeouts, duplicate requests, and concurrent race conditions.
</PROCEDURAL_WORKFLOW>
