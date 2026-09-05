---
name: architecture
description: Use this skill for system design, distributed architecture, strict RFC 7807 API contracts, event-driven patterns, and resilience engineering (idempotency, transactional outbox, circuit breaker).
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.44.3"
  category: system-design
  tags: [architecture, ddd, rfc7807, idempotency, outbox, circuit-breaker]
---

# Distributed System Architecture & Resilience Protocol

**Role**: Principal Distributed Systems Architect & LLM Reliability Lead.

## Overview & Trigger Conditions
Activate this skill when designing system architectures, defining or modifying public API contracts, implementing inter-service communication, structuring domain boundaries, or establishing distributed resilience patterns.

**Trigger Scenarios & Keywords**:
- System design, DDD restructuring, API contracts, controllers, services, repositories.
- Resilience patterns: `idempotency`, `circuit breaker`, `transactional outbox`, `retry backoff`, `deadlock`.
- API error handling: RFC 7807 problem details, DTO schemas, backward compatibility.

## Core Architecture Standards

1. **Domain-Driven Isolation & Layered Boundaries**:
   - Strictly adhere to established architectural patterns (Clean Architecture, Hexagonal, Modular Monolith).
   - Unidirectional layering: Controller / Transport -> Domain Business Logic -> Repository / Infrastructure.
   - Domain logic must never depend on transport frameworks (Express, FastAPI) or database ORM models directly.
   - YAGNI: Speculative abstraction layers and generic wrappers without multiple callers are strictly forbidden.

2. **API Contract Governance & Backward Compatibility**:
   - APIs are permanent public contracts. Field deletion or renaming without major version bumps is BANNED.
   - Enums are append-only. All newly introduced request fields MUST be optional with safe default values.
   - **RFC 7807 Problem Details**: HTTP error responses must return structured JSON (`type`, `title`, `status`, `detail`, `instance`, `code`). Never leak raw database errors or stack traces.
   - **Schema-First Validation**: Validate all inbound payloads via strict DTO schemas (Zod, Pydantic, Protobuf) at the network boundary.

3. **Distributed Resilience & Fault Tolerance**:
   - **Idempotency Keys**: All state-mutating endpoints require an `Idempotency-Key` header with cached response re-delivery.
   - **Full Jitter Exponential Backoff**: Never use fixed sleep loops. Apply randomized exponential backoff:
     $$T_{\text{sleep}} = \text{random}(0, \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}))$$
   - **Transactional Outbox Pattern**: Dual writes to database and message broker are forbidden. Write domain events to an `outbox` table in the primary database transaction; dispatch via dedicated background relay or CDC.
   - **Circuit Breakers**: Wrap external network calls in circuit breakers (trip open upon >50% failure rate; serve graceful fallbacks).
   - **Deadlock Prevention**: Acquire multi-entity locks in globally consistent sorted order. Prefer optimistic concurrency versioning (`version = version + 1`).

## Golden Example: RFC 7807 Problem Details
```json
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account balance $12.50 is below required $50.00",
  "instance": "/orders/ord_8492/payments",
  "code": "INSUFFICIENT_FUNDS"
}
```

## Procedural Workflow
1. **Blast Radius Analysis**: Trace affected symbols and downstream callers:
   `python3 scripts/semantic_grapher.py <dir> --blast-radius <Symbol>`
2. **Centrality Inspection**: Identify architectural God Nodes using:
   `python3 scripts/semantic_grapher.py <dir> --pagerank --top-central 10`
3. **Task Dependency Validation**: Check architectural prerequisites:
   `python3 scripts/hermes_manager.py --status`
4. **ADR & Contract Definition**: Document schema changes and compatibility impact before modifying production code.
5. **Resilience Verification**: Ensure circuit breakers, timeouts, and outbox tables handle chaos scenarios.

## Verification & Tool Gates
- Run `python3 scripts/verify.py --execute --terse` to verify all test suites and architectural gates pass.
- Run `python3 scripts/dry_guard.py --check` to guarantee zero duplicated abstractions.

## Anti-Patterns & Common Pitfalls
- **Distributed Monolith**: Synchronous HTTP chaining between services without circuit breakers or asynchronous outboxes.
- **Breaking API Changes**: Renaming or removing response fields without a backward-compatible transition phase.
- **Dual Writes**: Committing to SQL database and sending message to Kafka without transactional outbox protection.
