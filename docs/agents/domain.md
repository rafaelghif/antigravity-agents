# Domain Docs Configuration

How the engineering skills consume this repository's domain documentation.

## Layout: Single-Context

- **Living Domain Context**: [CONTEXT.md](file:///D:/Project/antigravity-agents/CONTEXT.md) at the repository root. Defines bounded contexts, core terminology, and domain boundaries.
- **Architectural Decisions**: [docs/adr/](file:///D:/Project/antigravity-agents/docs/adr) contains numbered ADR files (e.g. `0001-antigravity-5-tier-memory-system.md`).

## Consumption Rules

1. Before starting work touching domain logic or architecture, inspect [CONTEXT.md](file:///D:/Project/antigravity-agents/CONTEXT.md).
2. Use the exact vocabulary defined in the glossary. Avoid synonyms or conflicting jargon.
3. If an implementation decision conflicts with an existing ADR in `docs/adr/`, flag it explicitly before modifying code.
