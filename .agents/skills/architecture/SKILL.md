---
name: architecture
description: Use this skill when the user asks for system design, database schema alterations, API contract changes, or cross-module refactoring.
---

<CRITICAL_DIRECTIVE>
You must execute the Principal Architect procedural workflow and enforce Enterprise Scale before mutating any code.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Scalability (Big-O)**: Rigorously analyze the time and space complexity of loops, database queries, and caching strategies. Ensure operations scale linearly or logarithmically.
2. **Statelessness**: Enforce stateless service layers. Application servers must be capable of horizontal scaling behind a load balancer without localized state corruption.
3. **Database Performance**: Mandate index utilization for frequent queries. Actively prevent and eliminate N+1 query patterns in ORMs.
4. **Separation of Concerns**: Enforce strict module isolation (e.g., separating routing controllers, business domain logic, and data access layers).
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Impact Analysis**: Use code search (`grep_search`) to locate all consumers of the modified schema, interface, or module.
2. **Draft the Contract**: Write the proposed schema/API contract in a scratchpad artifact.
3. **Review against Constraints**:
   - Is it backwards compatible?
   - Does it violate existing bounded contexts in the project?
   - Does it introduce new stateful dependencies?
4. **Approval**: You MUST present an Architecture Decision Record (ADR) detailing the Blast Radius to the user and wait for approval before implementing the changes.
</PROCEDURAL_WORKFLOW>
