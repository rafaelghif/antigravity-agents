---
name: schema-manager
description: Single point of authority for documenting and cascading changes for database schemas and data dictionaries.
---
# Schema Manager Skill

## Objective
Eradicate AI hallucinations regarding database fields, tables, and architectures by maintaining a strict Single Source of Truth in `.agents/brain/schema.md`.

## When to Execute
- Any time a database migration is created, altered, or deleted.
- Any time a core data contract (e.g., API response interface) is modified.

## Execution Steps
0. **Pre-Migration**: Generate explicit `up` and `down` migration files (e.g., `migrations/YYYYMMDDHHMMSS_name.up.sql`). If an ORM is detected, use its native migration generator. Never alter DB state without a reversible migration script.
1. **Impact Analysis**: Delegate complex structural impact analysis to the `architecture-auditor` skill. For immediate field tracking, use `grep_search` to find ALL occurrences of the modified field.
2. **Update Codebase**: Safely refactor all found dependencies to match the new schema.
3. **Update Brain**: Overwrite or update `.agents/brain/schema.md` to reflect the exact new structure. You MUST append a `last_verified: YYYY-MM-DD` timestamp to the modified schema entities.
4. **Mandatory Testing**: Run or write unit tests to verify the schema change hasn't broken serialization or database queries. *Exception*: If this change is a critical `hotfix/`, adhere to the reduced testing protocol defined in AGENTS.md §3 (60% coverage + manual QA). The `last_verified` timestamp must also include a `(hotfix)` note.

## Zero-Assumption Rule
Never guess a field name. If a field is present in the codebase but absent from `schema.md`, treat it as **deprecated or undocumented**. Do NOT use it in new code. Instead, update `schema.md` first (via a migration) or escalate to the user.
