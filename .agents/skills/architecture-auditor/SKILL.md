---
name: architecture-auditor
description: Holistic Impact Analysis, blast radius, extensibility.
instruction: Use before implementing a new feature, adding an endpoint, or refactoring a core module to check blast radius and security.
requires_core: ">=4.0.0"
---
# Architecture Auditor Skill

## Objective
Enforce the "World-Class Engineering Mindset" defined in AGENTS.md (Holistic Impact checks).

## When to Execute
- BEFORE starting any medium-to-large feature implementation.
- BEFORE refactoring existing core modules.
- **Objective Skip Conditions (AND logic)**:
  - Code changes < 10 lines (excluding tests)
  - No new dependencies
  - No new endpoints/APIs
  - No schema changes
  - Test coverage remains >= current level
  If uncertain, produce a 2-line summary in `.agents/plans/audit-quick-<date>.md`.

## Execution Steps
1. Execute the Holistic Impact checks explicitly listed in AGENTS.md (Blast Radius, Future-Proofing, Reusability, Performance, Security).
2. Produce an "Audit Report" artifact inside `.agents/plans/audit-<slug>-<date>.md` before writing code.
3. Use the following explicit template for the report:
   - **Blast Radius**: Modules impacted directly/indirectly.
   - **Future-Proofing**: Number of hardcoded values > 3? Business logic vs. presentation mixed? API response fields not versioned? Constants used in > 5 files?
   - **Deprecation Debt**: Add scoring (1pt per deprecated API version, 3pt per unpatched CVE, 5pt for EOL within 12 months). Score > 10 → mandatory technical debt ticket creation.
   - **Reusability**: Shared utility extraction potential.
   - **Performance**: Algorithmic complexity and bottlenecks.
   - **Security**: Authentication, authorization, and data exposure.
   - **Mitigations**: Planned actions for identified risks.
