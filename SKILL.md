# Skill Architecture & DRY Rules

This document manages all domain-specific `.agents/skills/<name>/SKILL.md` files.

<DRY_TOKEN_OPTIMIZATION>
- **No Duplication**: If a rule exists in `AGENTS.md` or another `SKILL.md`, DO NOT repeat it here. Use markdown links instead.
- **Telegraphic**: Keep `SKILL.md` files < 50 lines. Remove generic instructions. Focus on precise code checks, API usages, or strict patterns.
- **Modular**: Each skill should focus on ONE explicit domain (e.g., `architecture`, `caveman`, `verification`).
</DRY_TOKEN_OPTIMIZATION>

<TARGET_PROJECT_FOCUS>
- `SKILL.md` files exist to help the agent write better code for the **TARGET PROJECT**, not to over-engineer the agent itself.
- All rules must anchor to tangible target project needs.
</TARGET_PROJECT_FOCUS>

<ANTI_HALLUCINATION>
- `SKILL.md` must enforce `grep_search` and `list_dir` for its specific domain. Example: Before applying a CSS grid, `grep_search` to see if a UI library like Tailwind is already used in the target project.
</ANTI_HALLUCINATION>

## Available Skills
Always consult the specific folder inside `.agents/skills/` for execution details.
- [api-contracts](file://.agents/skills/api-contracts/SKILL.md) -> API contract governance, RFC 7807, schema validation.
- [architecture](file://.agents/skills/architecture/SKILL.md) -> System design, domain boundaries, database schemas.
- [caveman](file://.agents/skills/caveman/SKILL.md) -> Token optimization & exact telegraphic outputs.
- [code-quality](file://.agents/skills/code-quality/SKILL.md) -> Enterprise maintainability, clean code, SOLID principles.
- [code-simplification](file://.agents/skills/code-simplification/SKILL.md) -> Eliminating over-engineering, flattening abstractions.
- [data-engineering](file://.agents/skills/data-engineering/SKILL.md) -> Database schemas, migrations, data pipelines.
- [design](file://.agents/skills/design/SKILL.md) -> UI components, styling, WCAG 2.2 AA accessibility.
- [devops](file://.agents/skills/devops/SKILL.md) -> Docker, Kubernetes, CI/CD, Infrastructure as Code.
- [dry](file://.agents/skills/dry/SKILL.md) -> Anti-duplication audit and deduplication.
- [mcp-setup](file://.agents/skills/mcp-setup/SKILL.md) -> Model Context Protocol setup and tool integration.
- [observability](file://.agents/skills/observability/SKILL.md) -> Logging, metrics, distributed tracing, audit trails.
- [performance-optimization](file://.agents/skills/performance-optimization/SKILL.md) -> Web Vitals, latency, bundle size optimization.
- [resilience-engineering](file://.agents/skills/resilience-engineering/SKILL.md) -> Idempotency keys, circuit breakers, deadlocks.
- [security](file://.agents/skills/security/SKILL.md) -> Authentication, RBAC, secret scanning, least privilege.
- [semantic-graphing](file://.agents/skills/semantic-graphing/SKILL.md) -> Codebase AST parsing and architecture mapping.
- [verification](file://.agents/skills/verification/SKILL.md) -> Test-driven validation, anti-sham testing strategies.
- [zero-downtime-migrations](file://.agents/skills/zero-downtime-migrations/SKILL.md) -> Expand-contract migrations, concurrent indexing.
