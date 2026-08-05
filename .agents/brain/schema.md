# Project Architecture & Schema Authority

*Single Source of Truth for database schemas, ORM models, API contracts, and Agent System State.*
*Last Verified*: 2026-08-05

## 1. Dynamic Schema Bootstrap Rule
- Whenever an ORM model (`schema.prisma`, `models.py`, `schema.sql`) or API contract is added to the application codebase, `system-architect` MUST infer and append the entity structure here or under `.agents/brain/schemas/<domain>.md`.

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
> [!NOTE] LOCAL PER-MACHINE TRAIL
> `audit.jsonl` is gitignored and therefore a **local, per-machine** execution trail. It does NOT provide cross-machine immutability. For shared audit history, rely on the Git history and the remote Issue/PR record.

```json
{
  "timestamp": "<ISO8601>",
  "task_slug": "<string>",
  "micro_task": "<string>",
  "status": "COMPLETED | FAILED | REVERTED",
  "token_usage": { "input": 0, "output": 0 }
}
```

### 2.4 Antigravity Workspace Customizations
- Workspace MCP configuration: `.agents/mcp_config.json`, with remote servers using `serverUrl`.
- Workspace skills: `.agents/skills/<name>.md` with YAML frontmatter containing `name` and `description`.
- Settings baseline: `.agents/antigravity-settings.example.json`; copy values into the global Antigravity CLI settings file.
- Compatibility metadata: `.agents/antigravity-compatibility.json` records the tested CLI version, docs baseline date, and official references.

### 2.5 Delivery State
```yaml
status: ACTIVE | COMPLETE
issue: <number>
commit: <sha>
pull_request: <number>
merge_commit: <sha>
release: <tag>
completed_at: <ISO8601>
```

An agent must not resume a plan with `status: COMPLETE`.
