---
name: world-class-programmer
description: Principles, workflows, and standards for writing clean, secure, and highly optimized code.
---

# World-Class Programming Skill

This playbook outlines advanced engineering practices, architectural guidelines, and optimization checklists to ensure code meets a world-class standard.

## 1. Core Engineering Principles
- **DRY (Don't Repeat Yourself)**: Abstract redundant patterns into reusable utilities, functions, or base classes.
- **SOLID Design**:
  - *Single Responsibility*: Every class/module must solve exactly one problem.
  - *Open/Closed*: Software entities should be open for extension but closed for modification.
  - *Liskov Substitution*: Subtypes must be substitutable for their base types.
  - *Interface Segregation*: Prefer many client-specific interfaces over one general-purpose interface.
  - *Dependency Inversion*: Depend on abstractions, not concretions.
- **KISS (Keep It Simple, Stupid)**: Minimize cognitive complexity. Avoid premature optimization or over-engineering.

## 2. Coding Guidelines
- **Robust Error Handling**: Never swallow exceptions. Always use specific exception types, log full stack traces when appropriate, and provide fallback actions.
- **Strong Typing**: Use type annotations/hints (e.g., Python typing) for all function arguments and return types to ensure static analysis viability.
- **Defensive Programming**: Validate inputs (types, value ranges, nullability) at public API boundaries.

## 3. Optimization Checklist
- **Algorithm Complexity**: Analyze time complexity (Big O) of loops and data structure operations. Prefer hashes/sets for $O(1)$ lookups instead of $O(N)$ list traversals.
- **Resource Management**: Always use context managers (`with` statements) to close files, database sessions, and sockets.
- **Memory Footprint**: Use generators for lazy evaluation when reading large datasets to avoid out-of-memory errors.
