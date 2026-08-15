---
name: architecture
description: Use this skill when the user asks for system design, database schema alterations, API contract changes, or cross-module refactoring.
---

<CRITICAL_DIRECTIVE>
You must execute the Principal Architect procedural workflow before mutating any code.
</CRITICAL_DIRECTIVE>

<PROCEDURAL_WORKFLOW>
1. **Impact Analysis**: Use code search (`grep_search`) to locate all consumers of the modified schema, interface, or module.
2. **Draft the Contract**: Write the proposed schema/API contract in a scratchpad artifact.
3. **Review against Constraints**:
   - Is it backwards compatible?
   - Does it violate existing bounded contexts in the project?
   - Does it introduce new stateful dependencies?
4. **Approval**: You MUST present an Architecture Decision Record (ADR) detailing the Blast Radius to the user and wait for approval before implementing the changes.
</PROCEDURAL_WORKFLOW>
