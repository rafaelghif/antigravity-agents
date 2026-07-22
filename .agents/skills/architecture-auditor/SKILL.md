---
name: architecture-auditor
description: Performs rigorous Holistic Impact Analysis (blast radius, DRY, SOLID, extensibility) before and after major code changes.
---
# Architecture Auditor Skill

## Objective
Enforce the "World-Class Engineering Mindset" defined in AGENTS.md §3.

## When to Execute
- BEFORE starting any medium-to-large feature implementation.
- BEFORE refactoring existing core modules.
- **Skip Condition**: If the change touches < 10 lines of code, is a trivial bugfix, or is a documentation-only change, you may skip the full audit. If uncertain, produce a 2-line summary in `.agents/plans/audit-quick-<date>.md`.

## Execution Steps
1. Execute the Holistic Impact checks explicitly listed in AGENTS.md §3 (Blast Radius, Future-Proofing, Reusability, Performance, Security).
2. Produce an "Audit Report" artifact inside `.agents/plans/audit-<slug>-<date>.md` before writing code.
3. Use the following explicit template for the report:
   - **Blast Radius**: Modules impacted directly/indirectly.
   - **Future-Proofing**: Generic solution vs hardcoded use case.
   - **Reusability**: Shared utility extraction potential.
   - **Performance**: O(n²) loops, N+1 queries, memory leaks.
   - **Security**: New endpoints, data exposure, input vectors.
   - **Mitigations**: Planned actions for identified risks.
