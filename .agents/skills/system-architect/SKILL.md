---
name: system-architect
description: System architecture auditor, database schema manager, and test data synthesizer. Triggers when auditing system impact, designing ORM schemas, migrating databases, or generating mock seed data.
requires_core: ">=4.3.0"
---
# System Architect Skill

## Objective
Single authority for architectural impact auditing, database schema governance, and synthetic data generation.

## 1. Holistic Impact Audit
- Trace blast radius across modules before making architectural modifications.
- Ensure public API backward compatibility; define migration strategies for breaking changes.

## 2. Schema Governance
- Single Source of Truth: Keep `.agents/brain/schema.md` or `.agents/brain/schemas/<domain>.md` synchronized whenever ORM models change (`prisma.schema`, `models.py`, `schema.sql`).
- Zero-Assumption Rule: Never guess column names, data types, or relationships without verifying the schema authority.

## 3. Data Synthesis
- Generate realistic mock datasets for database seeding and API tests.
- Ensure synthetic data respects schema constraints, foreign key relationships, and data privacy rules.
