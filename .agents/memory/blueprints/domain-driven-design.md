# Domain-Driven Design (DDD) Blueprint

This blueprint outlines standards for structuring domain-centric software systems, focusing on tactical design patterns.

## 1. Domain Modeling Terminology

- **Entity**: An object defined by its identity rather than its attributes (e.g., `User` with a unique ID).
- **Value Object**: An immutable object defined by its attributes (e.g., `Money` or `Address`). It has no identity.
- **Aggregate Root**: A cluster of associated objects treated as a single unit for data changes. External references must only point to the root.
- **Repository**: An interface providing access to collection-like operations for aggregates.
- **Domain Event**: Something that happened in the domain that you want other parts of the system to be aware of.

## 2. Directory Layout

```
src/
└── billing/                 # Bounded Context (Domain module)
    ├── domain/              # Aggregate roots, value objects, domain events
    │   ├── billing_account.py
    │   └── invoice.py
    ├── application/         # Commands, queries, and handlers
    │   ├── create_invoice.py
    │   └── payment_processor.py
    └── infrastructure/      # DB mappers, events publisher
        └── stripe_adapter.py
```

## 3. Implementation Rules
- Domain objects must guard their invariants (internal consistency) via encapsulation.
- Changes across Bounded Contexts must be eventually consistent, coordinated by **Domain Events** or integration message brokers.
