---
name: observability
description: Use this skill when implementing structured logging, metrics, distributed tracing, OpenTelemetry instrumentation, or system health monitoring.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.45.0"
  category: observability
  tags: [opentelemetry, logging, metrics, tracing, prometheus, red-method]
---

# Observability, Telemetry & Distributed Tracing Protocol

**Role**: Staff Site Reliability & Observability Engineer.

## Overview & Trigger Conditions
Activate this skill when implementing application logging, system metrics, distributed tracing, OpenTelemetry (OTel) instrumentation, service health checks, or agentic audit reporting.

**Trigger Scenarios & Keywords**:
- Distributed tracing, structured logging, Prometheus metrics, OpenTelemetry, audit logs.
- Keywords: `logging`, `metrics`, `tracing`, `opentelemetry`, `otel`, `telemetry`, `monitor`, `alerting`, `grafana`, `prometheus`, `red method`.

## Core Standards & Invariants

1. **OpenTelemetry (OTel) Standardization**:
   - Standardize strictly on OpenTelemetry SDKs and OTLP exporters for Logs, Metrics, and Tracing.
   - Do NOT bind directly to proprietary, vendor-locked SDKs. Emit vendor-neutral OTLP data over gRPC/HTTP.
   - Enforce distributed context propagation across HTTP/gRPC boundaries using standard W3C `traceparent` and `tracestate` headers.

2. **Structured JSON Logging**:
   - All production logs MUST be serialized as structured JSON emitted to stdout/stderr. Arbitrary string concatenation is strictly prohibited.
   - Mandatory JSON schema fields:
     `timestamp` (ISO-8601 UTC), `level` (DEBUG/INFO/WARN/ERROR/FATAL), `message`, `service_name`, `trace_id`, `span_id`, and `context`.
   - Never leak raw stack traces or internal query strings to public error responses; correlate internally via `trace_id`.

3. **RED Metrics Method (Rate, Errors, Duration)**:
   - For every HTTP endpoint or RPC handler, expose:
     - **Rate**: Inbound requests per second (`http_requests_total` counter).
     - **Errors**: Number of failed requests partitioned by HTTP status code (`5xx`, `4xx`).
     - **Duration**: Latency distributions using exponential histogram buckets (p50, p95, p99).
   - **Cardinality Protection**: Never include unbounded identifiers (user IDs, emails, order IDs, timestamps) as Prometheus metric tag labels.

4. **Security, Health & Agent Telemetry**:
   - Redact PII, bearer tokens, passwords, and authorization headers before serialization.
   - Distinguish between `/healthz` (liveness: process is running) and `/ready` (readiness: DB connections, caches, and queues are healthy).
   - For agentic systems, record token consumption, tool latencies, debate turns, and verification gate failures.

## Golden Example: Structured JSON Log Event
```json
{
  "timestamp": "2026-09-05T06:42:00Z",
  "level": "INFO",
  "message": "Order payment settled",
  "service_name": "checkout-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "context": {
    "order_id": "ord_9921",
    "amount_cents": 4500,
    "currency": "USD"
  }
}
```

## Procedural Workflow
1. **Telemetry Inspection**: Inspect active agent communication and governance metrics via:
   `python3 scripts/inbox_manager.py report`
2. **Instrument Pipeline**: Configure OpenTelemetry Tracer, Meter, and structured JSON formatters.
3. **Audit Trail Review**: Inspect agent audit records in `.agents/brain/global_audit.log`:
   `python3 scripts/memory_consolidator.py --show`
4. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Ad-hoc Console Output**: Leaving `console.log()` or `print()` statements in production code.
- **High-Cardinality Metric Labels**: Adding `user_id` or `email` as a label on a Prometheus metric.
- **Credential Leakage**: Logging full HTTP authorization headers or raw request payloads containing unmasked credentials.
