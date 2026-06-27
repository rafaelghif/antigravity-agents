---
name: adr
description: Standardized playbook and template for generating new Architectural Decision Records.
---

# Architectural Decision Records (ADR) Skill Playbook

This playbook provides templates and step-by-step instructions for adding architectural design logs.

## ADR Template
```markdown
# ADR [Number]: [Title]

## Context
[Describe the state of the codebase, problem statement, or design requirements.]

## Decision
[Outline the chosen solution, design pattern, or infrastructure component.]

## Status
[Draft | Accepted | Superseded]

## Consequences
[Describe positive and negative outcomes or future work required.]
```

## Review Protocol
- Ensure the ADR is placed under `.agents/memory/decisions/`.
- Ensure it is linked in the master architecture registry at `.agents/memory/architecture.md`.
