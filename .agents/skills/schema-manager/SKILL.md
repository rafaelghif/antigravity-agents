---
name: schema-manager
description: Single point of authority for database schemas and data dictionaries.
instruction: Use when creating migrations, altering DB state, or modifying core data contracts to update schema.md.
requires_core: ">=4.0.0"
---
# Schema Manager Skill

## Objective
Eradicate AI hallucinations regarding database fields, tables, and architectures by maintaining a strict Single Source of Truth in `.agents/brain/schema.md`.

## When to Execute
- Any time a database migration is created, altered, or deleted.
- Any time a core data contract (e.g., API response interface) is modified.

## Execution Steps
0. **Pre-Migration**: Generate explicit `up` and `down` migration files.
   - **Migration Naming**: `YYYYMMDDHHMMSS_<action>_<table>.sql` (Actions: `create`, `alter`, `drop`, `add_column`, `rename_column`).
   - **ORM Detection**: Check `package.json` (`typeorm`, `sequelize`, `prisma`, `drizzle`), `requirements.txt` (`sqlalchemy`, `django`), `Gemfile` (`rails`). Use native generator if found. Fallback to raw SQL.
   - **Dry-Run Protocol**: Always run migration with `--dry-run` first. Log to `.agents/scratch/migration-<date>.log`. Confirm via `ask_question` before executing (unless `!force`).
1. **Impact Analysis**: Delegate complex structural impact analysis to the `architecture-auditor` skill. For immediate field tracking, use `grep_search` to find ALL occurrences of the modified field.
2. **Update Codebase**: Safely refactor all found dependencies to match the new schema.
3. **Update Brain**: Overwrite or update `.agents/brain/schema.md` to reflect the exact new structure. You MUST append a `last_verified: YYYY-MM-DD` timestamp to the modified schema entities.
4. **Mandatory Testing**: Run or write unit tests to verify the schema change hasn't broken serialization or database queries. *Exception*: If this change is a critical `hotfix/`, adhere to the reduced testing protocol (60% coverage + manual QA). The `last_verified` timestamp must also include a `(hotfix)` note.

## Zero-Assumption Rule
Never guess a field name. If a field is present in the codebase but absent from `schema.md`: 
1. If this is an existing codebase where `schema.md` hasn't caught up, bootstrap the schema by verifying the actual database or ORM models and updating `schema.md`.
2. Otherwise, treat it as **deprecated or undocumented** and do NOT use it in new code. Instead, update `schema.md` first (via a migration) or escalate to the user.
