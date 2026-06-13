# ADR-002: Introduce Modular ADRs and Validation

- **Date**: 2026-06-14
- **Status**: Accepted

## Context
Architectural Decision Records (ADRs) were previously documented inside a monolithic `.agents/adr.md` file. As the workspace expands with more features, this monolithic file becomes cluttered, makes parsing difficult, and does not support granular tracking.

## Decision
Modularize the ADR structure:
1. Store individual ADR files inside `.agents/adrs/` with chronological numerical slug filenames (e.g., `002-introduce-modular-adrs-and-validation.md`).
2. Keep `.agents/adr.md` strictly as a high-level index map.
3. Introduce `./.agents/scripts/helper.sh create-adr <title> [status]` to automate ADR creation and index registration.
4. Add automated ADR compliance verification in `validate.sh` (Check 10).

## Consequences
- Workspace decisions are easily searchable, modular, and trackable.
- Automatically prevents committing incomplete ADRs containing placeholders.
- Simplifies bootstrapping and workspace upgrades.
