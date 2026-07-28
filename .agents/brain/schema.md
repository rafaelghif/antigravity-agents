# Project Architecture & Schema Authority

*Single Source of Truth for database schemas, ORM models, API contracts, and Agent System State.*
*Last Verified*: 2026-07-28

## 1. Dynamic Schema Bootstrap Rule
- Whenever an ORM model (`prisma.schema`, `models.py`, `schema.sql`) or API contract is added to the application codebase, `system-architect` MUST infer and append the entity structure here or under `.agents/brain/schemas/<domain>.md`.

## 2. Agent System Core Contracts

### 2.1 Task Plan Schema (`.agents/plans/<task-slug>.md`)
```markdown
# Plan: <Task Title>

## 1. Decisions & Architectural Trade-offs
- Key decisions, invariants, and context limits.

## 2. Granular Micro-Tasks
### Phase <N>: <Phase Title>
- [ ] **Micro-Task <Phase.Item>**: <Detailed Description with Target Files & Verification Rules>
```

### 2.2 Atomic POSIX Lock Metadata (`.agents/locks/<md5_hash_of_filepath>.lock/owner.json`)
```json
{
  "claimed_by": "<agent_id_or_subagent_id>",
  "claimed_at": "<ISO8601_Timestamp>",
  "target_filepath": "<absolute_or_relative_path>"
}
```

### 2.3 Audit Log Schema (`.agents/brain/audit.jsonl`)
```json
{
  "timestamp": "<ISO8601>",
  "task_slug": "<string>",
  "micro_task": "<string>",
  "status": "COMPLETED | FAILED | REVERTED",
  "token_usage": { "input": 0, "output": 0 }
}
```




