# Project Architecture & Schema Authority

*Single Source of Truth for database schemas, ORM models, and API contracts.*
*Last Verified*: 2026-07-27

## 1. Agent Core Mutex Schema (`.agents/brain/state.json`)
```json
{
  "claimed_tasks": {
    "file_path": {
      "claimed_by": "string (subagent_id / orchestrator)",
      "claimed_at": "ISO8601 Timestamp"
    }
  },
  "last_updated": "ISO8601 Timestamp"
}
```

## 2. Dynamic Schema Bootstrap Rule
- Whenever an ORM model (`prisma.schema`, `models.py`, `schema.sql`) or API contract is added to the application codebase, `system-architect` MUST infer and append the entity structure here or under `.agents/brain/schemas/<domain>.md`.


