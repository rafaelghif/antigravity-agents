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
5. **Future-Proof Data Modeling**: Never design rigid schemas. Anticipate evolutionary changes (e.g., what if entity A merges with B? What if C is added later?). Use Domain-Driven Design (DDD), interfaces, and abstract repository patterns so the domain logic isn't coupled to the DB.
6. **Extensibility & Polymorphism**: Build plugin-ready architecture. If you think the user might add more types later, use polymorphic associations or Strategy Patterns instead of hardcoded `if/else` ladders.
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


<L9_STANDARDS>
- **Micro-services / Event-Driven**: Bias towards decoupled architectures. Use Pub/Sub, queues, or Event Sourcing where applicable.
- **Statelessness**: REST APIs must be strictly stateless.
- **Pro-Tier Mandatory**: System design mandates the highest reasoning. Subagents invoking this skill MUST use `Model: pro`.
</L9_STANDARDS>
