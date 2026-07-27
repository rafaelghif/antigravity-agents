# Project Architecture & Schema Authority

*Single Source of Truth for database schemas, ORM models, and API contracts.*
*Last Verified*: 2026-07-27

## 1. Agent Core State Schema (`.agents/brain/state.json`)
```json
{
  "session_id": "string | null",
  "current_branch": "string",
  "active_task": "string | null",
  "current_tier": "Tier 1 | Tier 2 | Tier 3",
  "current_step": "string",
  "token_usage": {
    "current_used": "number",
    "max_budget": "number",
    "last_compaction_timestamp": "string | null"
  },
  "active_subagents": ["string"],
  "claimed_tasks": { "task_key": "agent_id" },
  "last_updated": "ISO8601 Timestamp"
}
```

## 2. Dynamic Schema Bootstrap Rule
- Whenever an ORM model (`prisma.schema`, `models.py`, `schema.sql`) or API contract is added to the application codebase, `system-architect` MUST infer and append the entity structure here or under `.agents/brain/schemas/<domain>.md`.


