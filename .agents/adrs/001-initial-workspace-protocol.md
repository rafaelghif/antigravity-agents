# ADR-001: Initial Workspace Protocol Adoption

- **Date**: 2026-06-13
- **Status**: Accepted

## Context
The workspace needs a structured operational protocol for AI engineering agents to ensure version alignment, zero-hallucination execution, and high token efficiency.

## Decision
Adopt the Antigravity Agent Core (AAC) protocol, establishing `AGENTS.md` and the `.agents/` structure containing locks, rules, schemas, and active task memory ledgers.

## Consequences
Developers and agents must follow strict bootstrapping sequences and use the helper scripts/Git hooks for validated, atomic commits.
