---
name: observability
description: Guidelines for implementing structured logging, distributed tracing (OpenTelemetry), performance metrics, and centralized error telemetry.
---

# Observability & Telemetry Skill Playbook

This playbook establishes the enterprise-grade practices for implementing observability, structured logging, distributed tracing, and metrics tracking inside software projects.

---

## 1. Structured Logging Standards

Enterprise applications must emit logs in a machine-readable format to enable searchability and analysis in central log aggregators (e.g. ELK stack, Datadog).

### A. Format Requirements
- **JSON Format**: Output all logs in JSON format in production.
- **Log Levels**: 
  - `DEBUG`: Verbose diagnostics (disabled by default in production).
  - `INFO`: Normal operational events (e.g. request started, job completed).
  - `WARN`: Unexpected but non-fatal conditions (e.g. slow response, cache miss).
  - `ERROR`: Runtime errors needing immediate investigation (includes stack trace).
  - `FATAL`: Critical system failure causing application shutdown.

### B. Standard Fields
Every log line must include:
- `timestamp`: UTC ISO-8601 format (`YYYY-MM-DDTHH:mm:ss.sssZ`).
- `level`: Log severity.
- `message`: Descriptive human-readable message.
- `correlation_id`: Unique request or transaction identifier.
- `module`: File or package namespace.

### C. Security Boundaries
- **NEVER** log sensitive personal information (PII) like emails, addresses, or phone numbers.
- **NEVER** log secrets, passwords, bearer tokens, authorization headers, or database credentials.

---

## 2. Distributed Tracing (OpenTelemetry)

Distributed tracing allows developers to track requests as they flow across multiple servers, databases, and microservices.

### A. Context Propagation
- **Correlation Context**: Ensure every incoming HTTP request or message queue task extracts the parent trace context (W3C Trace Context standard).
- **Context Injection**: Inject trace context headers (`traceparent`) into all outgoing external HTTP requests, gRPC calls, or message queue tasks.

### B. Instrumentation Checklist
- **Database Spans**: Automatically trace database queries to detect slow-running transactions.
- **HTTP Clients**: Trace outbound network calls to identify external dependency latency.
- **Long-Running Jobs**: Wrap background task executions (e.g. Celery, Cron) in spans.

---

## 3. Metrics Tracking

Use standard application metrics to measure service health, performance, and saturation.

### A. The RED Method (Request-scoped services)
Track:
1. **Rate**: Number of requests processed per second (RPS).
2. **Errors**: Number of failed requests per second.
3. **Duration**: Time taken to process requests (measure percentiles: p50, p90, p99).

### B. The USE Method (System resource monitoring)
Track:
1. **Utilization**: Percentage of resource capacity used (e.g. CPU, RAM, Disk).
2. **Saturation**: Extra work that the resource cannot process yet (e.g. request queues, thread pool queues).
3. **Errors**: System-level resource errors.

---

## 4. Error Telemetry & Alerting

Graceful error capturing prevents silent failures and helps maintain system stability.

- **Centralized Handlers**: Wrap top-level route controllers or execution loops in try-except statements that report uncaught exceptions to telemetry providers (e.g. Sentry, Datadog).
- **Enriched Context**: Attach custom tags (e.g. `user_id`, `tenant_id`, `environment`) to error reports to accelerate troubleshooting.
- **Alert Fatigue Prevention**: Define alert policies only for critical anomalies (e.g. HTTP 5xx rate > 1%) rather than transient failures.
