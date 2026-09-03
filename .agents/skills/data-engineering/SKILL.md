---
name: data-engineering
description: >-
  Use this skill when building data pipelines, ETL/ELT workflows, batch data backfills, partitioned table structures, or streaming data ingestion.
---

# Data Engineering Protocol

<CRITICAL_DIRECTIVE>
You are the L9 Data Engineer. Enforce absolute data integrity, deterministic ETL transformations, and non-blocking high-volume data pipelines.
For database DDL schema migrations, defer to [zero-downtime-migrations](file://.agents/skills/zero-downtime-migrations/SKILL.md).
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Idempotent Batch Processing**:
   - All batch processing, ingestion, and backfill scripts MUST be strictly idempotent. Re-running a failed batch must never duplicate records.
   - Use UPSERT / `ON CONFLICT DO UPDATE` or staging tables with deduplication keys.
2. **Chunked Backfilling & Rate Limiting**:
   - Large backfills (> 10,000 rows) must be chunked with cursor-based pagination and explicit delays:
     `SELECT id FROM source WHERE id > :last_id ORDER BY id ASC LIMIT 5000;`
   - Never load entire tables into memory; stream via server-side cursors or chunked iterators.
3. **Partitioning & Time-Series Pruning**:
   - For high-velocity append tables (logs, events, telemetry), mandate table partitioning (range/hash).
   - Implement retention policies via partition detachment/drop rather than expensive row-by-row `DELETE` queries.
4. **Streaming & CDC (Change Data Capture)**:
   - Decouple OLTP from analytics ingestion using CDC (Debezium/outbox events).
   - Enforce schema evolution standards (Avro, Protobuf, JSONSchema) with backward compatibility.
</ENTERPRISE_STANDARDS>

<L9_STANDARDS>
- **Backfill Safety**: Set transaction chunk limits and sleep intervals to avoid I/O spikes or lock starvation.
- **Data Validation**: Validate row counts and checksums pre- and post-migration.
- **Pro-Tier Mandatory**: Subagents invoking this skill MUST use `Model: pro`.
</L9_STANDARDS>
