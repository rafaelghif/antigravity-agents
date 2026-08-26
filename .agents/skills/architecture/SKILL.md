---
name: architecture
description: Use this skill when the user asks for system design, database schema alterations, API contract changes, or cross-module refactoring.
---

<CRITICAL_DIRECTIVE>
You must execute the Principal Architect procedural workflow and enforce Enterprise Scale before mutating any code.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Architectural Harmony**: All modules must conform to the project's established architectural style (Clean Architecture, Hexagonal, Layered MVC, or Feature-Sliced). Never introduce architectural dissonance.
2. **DRY Abstractions & Shared Services**: Extract shared domain rules, cross-cutting concerns (logging, auth, metrics), and database transactions into unified service layers.
3. **Scalability (Big-O)**: Rigorously analyze time and space complexity of loops, database queries, and caching strategies. Ensure operations scale linearly or logarithmically.
4. **Statelessness & Idempotency**: Application service layers must be strictly stateless and horizontally scalable. Write idempotent mutations for retriable operations.
5. **Database Performance & Anti-N+1**: Mandate index utilization for frequent queries. Actively prevent and eliminate N+1 query patterns in ORMs via eager loading/joins.
6. **Separation of Concerns & DDD**: Maintain strict isolation between controllers, business domain logic, and data access layers. Use abstract repository patterns.
7. **Extensibility & Polymorphism**: Build plugin-ready architecture. Use polymorphic associations or Strategy Patterns instead of brittle `if/else` ladders.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Architectural Discovery**: Analyze existing project structures using `grep_search` or `scripts/semantic_grapher.py` to identify established conventions.
2. **Impact & Blast Radius Analysis**: Locate all consumers of the modified schema, interface, or module.
3. **Draft Unified Contract**: Write the proposed schema/API contract adhering strictly to existing project naming, validation, and DTO standards.
4. **Review against Constraints**:
   - Is it backwards compatible?
   - Does it violate existing bounded contexts in the project?
   - Does it introduce new stateful dependencies or duplicate logic?
5. **Approval**: You MUST present an Architecture Decision Record (ADR) detailing the Blast Radius to the user and wait for approval before implementing the changes.
</PROCEDURAL_WORKFLOW>


<L9_STANDARDS>
- **Micro-services / Event-Driven**: Bias towards decoupled architectures. Use Pub/Sub, queues, or Event Sourcing where applicable.
- **Statelessness**: REST APIs must be strictly stateless.
- **Pro-Tier Mandatory**: System design mandates the highest reasoning. Subagents invoking this skill MUST use `Model: pro`.
</L9_STANDARDS>
