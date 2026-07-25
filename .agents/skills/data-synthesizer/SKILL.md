---
name: data-synthesizer
description: Generates realistic mock data and database seeds for UI/API testing.
instruction: Use when the database is empty and realistic data is needed to verify functionality or UI presentation.
requires_core: ">=4.1.4"
---
# Data Synthesizer Skill

## Objective
To inject realistic, varied, and edge-case inclusive mock data into the application so that the agent and developers can accurately test user interfaces, pagination, and API responses.

## When to Execute
- After running schema migrations on an empty database.
- When requested to test a UI component that depends on lists, charts, or user profiles.
- When building API endpoints that require robust dummy data.

## Execution Steps

1. **Schema Contextualization**:
   - Call the `schema-manager` to read the exact data types, constraints, and relationships of the target tables.
   
2. **Mock Generation Strategy**:
   - Identify the stack's native seeder framework (e.g., Laravel Seeders, Prisma Studio, Python Faker, Django Fixtures).
   - If a framework exists, write seeder scripts utilizing libraries like Faker to generate realistic names, addresses, and emails.
   - Ensure the generated data includes edge cases (very long strings, nulls, special characters) to stress-test the UI.

3. **Injection**:
   - Execute the seeder scripts to populate the local database.
   - Verify insertion success by querying a sample of the data.

4. **Cleanup Protocol**:
   - Ensure mock generation scripts are placed in proper development directories (e.g., `database/seeders`) and NEVER executed in production environments.
