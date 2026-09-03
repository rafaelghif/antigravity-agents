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
- [architecture](file://.agents/skills/architecture/SKILL.md) -> System design, domain boundaries, RFC 7807 contracts, outbox resilience & idempotency.
- [caveman](file://.agents/skills/caveman/SKILL.md) -> Token optimization & exact telegraphic outputs.
- [code-quality](file://.agents/skills/code-quality/SKILL.md) -> Enterprise maintainability, clean code, SOLID principles, early returns, DRY deduplication.
- [data-engineering](file://.agents/skills/data-engineering/SKILL.md) -> Database schemas, zero-downtime expand-contract migrations, concurrent DDL, ETL/CDC.
- [deep-research](file://.agents/skills/deep-research/SKILL.md) -> Epistemic web research, official documentation lookup, API contract verification.
- [design](file://.agents/skills/design/SKILL.md) -> UI components, styling, WCAG 2.2 AA accessibility, DTCG tokens, Core Web Vitals.
- [devops](file://.agents/skills/devops/SKILL.md) -> Docker, Kubernetes, CI/CD, Infrastructure as Code, Model Context Protocol (MCP).
- [observability](file://.agents/skills/observability/SKILL.md) -> Logging, metrics, distributed tracing, audit trails.
- [security](file://.agents/skills/security/SKILL.md) -> Authentication, RBAC/PBAC, secret scanning, least privilege.
- [semantic-graphing](file://.agents/skills/semantic-graphing/SKILL.md) -> Codebase AST parsing, blast radius, and architecture mapping.
- [verification](file://.agents/skills/verification/SKILL.md) -> Test-driven validation, anti-sham testing strategies.
