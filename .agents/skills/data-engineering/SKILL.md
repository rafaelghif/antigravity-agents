---
name: data-engineering
description: Use this skill for database schemas, zero-downtime expand-contract migrations, concurrent indexing, ETL/ELT data pipelines, and streaming CDC.
---

# Database & Data Engineering Protocol

<CRITICAL_DIRECTIVE>
Enforce absolute data integrity, non-blocking high-volume data pipelines, and zero-downtime database migrations. Migrations must never lock production tables or break running application instances.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Zero-Downtime Expand / Contract Pattern**:
   - Breaking schema changes (renames, column splits, type migrations) MUST follow a 3-phase rollout:
     - **Phase 1 (Expand)**: Add new column as nullable. Deploy app dual-writing to both old and new columns.
     - **Phase 2 (Backfill & Switch)**: Asynchronously backfill historical rows in rate-limited batches. Switch app reads to new column.
     - **Phase 3 (Contract)**: Remove dual-write logic and safely drop old column.
   - Column Renames: In-place `ALTER TABLE ... RENAME` is strictly banned in production.
2. **Non-Blocking DDL & Lock Timeouts**:
   - Indexes: ALWAYS use `CREATE INDEX CONCURRENTLY` (or database equivalent). Never use blocking plain `CREATE INDEX`.
   - Constraints: Add foreign keys/check constraints with `NOT VALID`, then validate in a separate non-blocking statement.
   - Strict Timeouts: Set explicit lock timeouts (`SET lock_timeout = '2s'; SET statement_timeout = '30s';`) to prevent connection pool exhaustion.
3. **Idempotent Batch Processing & Chunking**:
   - All batch backfills and data ingestion scripts MUST be idempotent (`ON CONFLICT DO UPDATE` or staging tables).
   - Large backfills (> 10,000 rows) must be chunked with cursor-based pagination and sleep intervals to avoid I/O spikes:
     `SELECT id FROM source WHERE id > :last_id ORDER BY id ASC LIMIT 5000;`
   - Stream rows via server-side cursors; never load entire datasets into memory.
4. **Partitioning & Time-Series Pruning**:
   - For high-velocity append tables (logs, events, metrics), enforce table partitioning (range/hash).
   - Prune expired data by dropping or detaching partitions, avoiding massive row-by-row `DELETE` locks.
5. **Streaming & CDC (Change Data Capture)**:
   - Decouple OLTP from analytics ingestion using CDC (Debezium/outbox events). Enforce schema evolution standards (Avro/Protobuf/JSONSchema).
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Lock & Table Footprint Analysis**: Determine if migration acquires an `ACCESS EXCLUSIVE` table lock.
2. **Phase Migration**: Deconstruct into backwards-compatible expand/contract stages.
3. **Execute & Backfill**: Apply with explicit `lock_timeout`, concurrent indexing, and chunked cursor-based backfills.
4. **Data Validation**: Validate row counts and checksums pre- and post-migration.
</PROCEDURAL_WORKFLOW>
