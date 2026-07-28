# Project Architecture & Schema Authority

*Single Source of Truth for database schemas, ORM models, and API contracts.*
*Last Verified*: 2026-07-27

## 1. Dynamic Schema Bootstrap Rule
- Whenever an ORM model (`prisma.schema`, `models.py`, `schema.sql`) or API contract is added to the application codebase, `system-architect` MUST infer and append the entity structure here or under `.agents/brain/schemas/<domain>.md`.



