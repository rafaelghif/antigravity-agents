---
name: data-engineering
description: Use this skill for database schemas, zero-downtime expand-contract migrations, concurrent indexing, ETL/ELT data pipelines, and streaming CDC.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.44.3"
  category: data-engineering
  tags: [database, migrations, expand-contract, cdc, indexing, etl]
---

# Database & Data Engineering Protocol

**Role**: Database SRE & Data Platform Reliability Lead.

## Overview & Trigger Conditions
Activate this skill when creating or modifying database schemas, writing database migrations, developing ETL/ELT data pipelines, performing batch data backfills, or configuring streaming Change Data Capture (CDC).

**Trigger Scenarios & Keywords**:
- Database schema changes, migrations, indexing, table partitioning, batch data jobs.
- Keywords: `database`, `db`, `schema`, `migration`, `table`, `index`, `etl`, `elt`, `pipeline`, `cdc`, `debezium`, `kafka`, `backfill`, `partitioning`.

## Core Standards & Invariants

1. **Zero-Downtime Expand / Contract Pattern**:
   - Breaking schema changes (column renames, type conversions, table splits) MUST follow a 3-phase rollout:
     - **Phase 1 (Expand)**: Add the new column/table as nullable. Deploy application code that dual-writes to both old and new targets.
     - **Phase 2 (Backfill & Switch)**: Asynchronously backfill historical data in rate-limited batches. Switch application reads to the new column/table.
     - **Phase 3 (Contract)**: Remove dual-write logic in the application. Safely drop the old column/table in a subsequent release.
   - In-place `ALTER TABLE ... RENAME COLUMN` is strictly forbidden in production.

2. **Non-Blocking DDL & Lock Timeouts**:
   - **Indexes**: ALWAYS use non-blocking creation syntax (`CREATE INDEX CONCURRENTLY` in PostgreSQL). Never block table writes with plain `CREATE INDEX`.
   - **Constraints**: Add foreign keys and check constraints with `NOT VALID`, then validate them in a separate non-blocking statement (`VALIDATE CONSTRAINT`).
   - **Lock Timeouts**: Every migration script MUST specify explicit lock and statement timeouts:
     ```sql
     SET lock_timeout = '2s';
     SET statement_timeout = '30s';
     ```
     This prevents queued DDL from blocking production query connection pools.

3. **Idempotent Batch Processing & Chunking**:
   - All batch backfills and data ingestion scripts MUST be idempotent (`ON CONFLICT DO UPDATE` or staging tables).
   - Large backfills (> 10,000 rows) must be chunked using cursor-based pagination and sleep intervals to avoid I/O spikes:
     ```sql
     SELECT id FROM source WHERE id > :last_id ORDER BY id ASC LIMIT 5000;
     ```
   - Stream rows via server-side cursors; never load full datasets into memory.

4. **Table Partitioning & Streaming CDC**:
   - For high-velocity append-only tables (logs, events, metrics), enforce range or hash partitioning.
   - Prune expired data by dropping or detaching old partitions (`ALTER TABLE ... DETACH PARTITION`), avoiding row-by-row `DELETE` lock contention.
   - Decouple OLTP databases from analytical ingestion using CDC (Debezium, outbox events, Kafka).

## Golden Example: Safe Non-Blocking PostgreSQL Migration
```sql
-- Phase 1 (Expand): Lock timeout + non-blocking index
SET lock_timeout = '2s';
SET statement_timeout = '30s';

ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_uuid UUID;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_uuid 
ON orders (customer_uuid);
```

## Procedural Workflow
1. **Lock & Footprint Analysis**: Evaluate whether proposed DDL acquires an `ACCESS EXCLUSIVE` table lock.
2. **Phase Migration**: Deconstruct schema changes into backward-compatible expand/contract stages.
3. **Execute & Backfill**: Apply non-blocking DDL with lock timeouts and chunked cursor-based backfills.
4. **Data Validation**: Validate row counts, nullability checks, and data checksums pre- and post-migration.
5. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Table Lock Starvation**: Running `ALTER TABLE ADD COLUMN ... DEFAULT <non-null>` on legacy DB engines without checking table locks.
- **Unbounded Bulk Updates**: Executing single-transaction `UPDATE table SET ...` on millions of rows, blowing up write-ahead logs (WAL) and causing replication lag.
- **Missing Rollback Script**: Writing forward migrations without corresponding, tested down-migrations.
