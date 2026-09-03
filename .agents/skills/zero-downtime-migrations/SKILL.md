---
name: zero-downtime-migrations
description: >-
  Use this skill when creating or modifying database schemas, writing DDL migrations, creating indexes concurrently, or performing non-blocking table alterations.
---

# Zero-Downtime Database Migration Protocol

<CRITICAL_DIRECTIVE>
Database migrations must never lock production tables, block active queries, or break running application pods during rolling deployments.
</CRITICAL_DIRECTIVE>

<CORE_STANDARDS>
1. **Expand / Contract (Parallel Run) Pattern**:
   - Breaking changes (column renames, type changes, table splits) MUST be split into 3 distinct release phases:
     - **Phase 1 (Expand)**: Add new column as nullable. Deploy app reading old column and dual-writing to both old and new.
     - **Phase 2 (Backfill & Switch)**: Asynchronously backfill historic rows in batches. Deploy app reading from new column.
     - **Phase 3 (Contract)**: Drop dual-write trigger and remove old column safely.

2. **Postgres Concurrent Operations**:
   - Indexes: ALWAYS use `CREATE INDEX CONCURRENTLY` or `DROP INDEX CONCURRENTLY`. Never block reads/writes with plain `CREATE INDEX`.
   - Constraints: Add foreign keys and check constraints using `NOT VALID`, then validate in a separate step: `ALTER TABLE ... VALIDATE CONSTRAINT ...`.

3. **Strict Lock Timeouts**:
   - Every migration script MUST set explicit lock and statement timeouts:
     ```sql
     SET lock_timeout = '2s';
     SET statement_timeout = '30s';
     ```
   - Prevents a blocked DDL query from queueing behind long transactions and exhausting connection pools.

4. **Safe Column Additions & Defaults**:
   - Never run `ALTER TABLE ... ADD COLUMN ... NOT NULL` without a default value in Postgres < 11.
   - For computed columns or foreign keys, add nullable first, backfill in chunks (e.g. 5,000 rows with `LIMIT/OFFSET` + sleep), then add `NOT NULL` constraint.

5. **Column / Table Renames**:
   - Banned: In-place `ALTER TABLE ... RENAME COLUMN ...`. Old application pods will crash immediately upon execution.
   - Follow the Expand/Contract dual-write lifecycle.
</CORE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Analyze Lock Footprint**: Determine if migration acquires an `ACCESS EXCLUSIVE` table lock.
2. **Phase Migration**: Deconstruct into backwards-compatible expand/contract stages.
3. **Execute Safely**: Apply with explicit `lock_timeout` and concurrent indexes.
</PROCEDURAL_WORKFLOW>
