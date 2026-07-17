# Project Architecture Blueprint: test-proj

## 1. Stack Details
- **Language/Platform**: Python
- **Pattern**: CLEAN Architecture
- **Framework/Library**: None
- **Database**: None
- **Infrastructure**: None

## 2. Directory Layout
- `src/`: Core codebase.
- `tests/`: Unit and integration testing suite.

## 3. Structural Rules
- Modules must communicate only through defined APIs.
- Domain entities must have zero external dependencies.
- **AI-Driven State Resolution**: If the agent detects a data contract mismatch, missing specification, or procedural conflict, it MUST halt operations, query this schema as the absolute source of truth, and logically self-correct without waiting for or relying on local script interventions.

## 4. Database Schema Registry

All active databases, their engines, tables, fields, indexes, and relationships must be documented here.

### Database: `[database_name]`
* **Engine**: [SQLite | PostgreSQL | MySQL | Redis | etc.]
* **Scope**: [Local | Containerized | Managed RDS | etc.]

#### Table: `[table_name]`
*Description of table purpose.*

| Field Name | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `id` | UUID/INT | PK | No | - | Primary Key |
| `field_name` | VARCHAR(255) | - | Yes | NULL | Field description |

**Indexes:**
* `idx_table_field`: [Type, e.g., BTREE] on `(field_name)`

**Foreign Keys / Relationships:**
* `target_field` -> `other_table.other_field` (Cascade / Restrict)

**Cross-Module References:**
* Link to other schema module files: e.g., Billing Schema (`.agents/schemas/billing.md`)
