---
name: database-evolution
description: Playbook for writing safe database migrations, managing schema evolutions, executing reversible rollbacks, and avoiding table lock contention in enterprise environments.
---

# Database Evolution & Schema Migration Playbook

This playbook establishes the engineering rules for migrating and evolving relational database schemas in enterprise applications with zero downtime and minimal table lock contention.

---

## 1. Zero-Downtime Migration Patterns

Relational database migrations must be designed so that the application can run continuously while the database is updated.

### A. The Expand and Contract Pattern
Never perform destructive changes (renaming columns, deleting columns, changing types) in a single step. Use a multi-stage rollout:
1. **Expand**: Add the new column/table. The application code starts dual-writing to both the old and new columns.
2. **Backfill**: Run a background batch script to migrate existing legacy data from the old column to the new column.
3. **Transition**: Update application readers to point to the new column. Remove writes to the old column.
4. **Contract**: Safely drop the old column/table in a separate release.

---

## 2. Reversible Migrations & Rollback Scripts

Every database migration MUST be fully reversible.

- **Up & Down Scripts**: Every migration file must contain both an `Up` script (applying changes) and a `Down` script (rolling back changes).
- **No Data Loss on Down**: Rollback scripts must never lead to untracked data loss. If a column is dropped in the `Up` step, ensure it was backed up or that the rollback script restores the schema structure safely.
- **Dry-run Verification**: Before applying migrations on target databases, run a local migration dry-run and verify rollback:
  - **Laravel/PHP**: `php artisan migrate:fresh` followed by tests.
  - **Django/Python**: `python manage.py migrate` and verify rollback using test suites.
  - **Node.js (Prisma)**: Use `npx prisma migrate dev` and verify down migrations if using custom SQL.
  - **Node.js (TypeORM/Sequelize)**: Run `typeorm migration:run` / `sequelize db:migrate` and test the `down` methods.
  - **Go (GORM/golang-migrate)**: Run `migrate -path db/migrations -database $DB_URL up` and `down` to verify reversibility.
  - **Java (Flyway/Liquibase)**: Use `mvn flyway:migrate` and `mvn flyway:undo` to validate rollback paths.

---

## 3. Avoiding Table Lock Contention

On large enterprise databases (tables with millions of rows), adding columns or indexes can lock the entire table, causing application outages.

- **Adding Columns with Defaults**: Never add a column with a default value directly on a large table in PostgreSQL or MySQL, as it forces a full-table rewrite. Add the column as nullable first, then set the default, and backfill existing rows in batches.
- **Safe Index Creation**:
  - In PostgreSQL, always use `CREATE INDEX CONCURRENTLY` to avoid locking writes on the table.
  - In MySQL, leverage online DDL algorithms: `ALGORITHM=INPLACE, LOCK=NONE`.
- **Foreign Key Constraints**: Adding a foreign key constraint can lock both target tables. Validate foreign keys using `NOT VALID` in PostgreSQL, then validate them in the background via `VALIDATE CONSTRAINT`.

---

## 4. Documentation & Schema Synchronization Protocol

To prevent context drift and hallucinated data structures across agent sessions, the agent MUST strictly conform to the following schema documentation protocol:

### A. Documenting New Structures
Whenever a new database, table, or field is discussed, proposed, or implemented, the agent MUST immediately update `.agents/schema.md` (or a modular schema file under `.agents/schemas/` indexed in `.agents/schema.md`) BEFORE proceeding with code changes.

### B. Schema Documentation Format
Every table entry MUST include:
1. **Engine and Scope**: The database engine (e.g. SQLite, PostgreSQL) and hosting environment.
2. **Schema Table**: A Markdown table with fields: `Field Name`, `Type`, `Key` (PK/FK), `Nullable` (Yes/No), `Default`, and a detailed `Description`.
3. **Indexes**: Clear list of indices with their types and columns.
4. **Foreign Keys & Cascades**: Explicit relationship mapping.
5. **Cross-Module References**: Hyperlinks to other related schema markdown files.

### C. Modifying Existing Schemas
If a field is renamed, added, or deleted, or if a table type/index is adjusted:
1. Update the schema table in `.agents/schema.md` or the corresponding `.agents/schemas/*.md` file.
2. Link the modification to the corresponding issue/ticket (e.g., `Refs: issue-XXX`).
3. Commit the schema updates alongside or before the migration scripts.
