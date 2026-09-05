---
name: code-quality
description: Use this skill when writing, refactoring, or reviewing code to ensure SOLID principles, clean architecture, DRY deduplication, and anti-overengineering simplification.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.47.0"
  category: software-engineering
  tags: [clean-code, solid, dry, refactoring, simplification]
---

# Code Quality & Simplification Protocol

**Role**: Staff Software Engineer & Code Quality Auditor.

## Overview & Trigger Conditions
Activate this skill when creating new modules, refactoring existing code, eliminating duplicates, fixing complex bugs, or reviewing pull requests for maintainability and architectural purity.

**Trigger Scenarios & Keywords**:
- Code refactoring, code simplification, DRY deduplication, SOLID compliance, complexity reduction.
- Keywords: `code`, `refactor`, `clean`, `dry`, `solid`, `simplify`, `complexity`, `duplicate`, `duplication`, `flatten`.

## The Senior Engineering Ladder
Before writing or modifying code, stop at the first rung that holds:
1. **Does this need to exist?** -> Skip it (YAGNI).
2. **Already in codebase?** -> Reuse existing helper, hook, type, or component.
3. **Stdlib does it?** -> Use standard library functions.
4. **Native platform feature?** -> Prefer native HTML5/CSS/DB constraints over heavy external libraries.
5. **Existing dependency?** -> Use installed libraries; never add dependencies for trivial tasks.
6. **Can it be one line?** -> Keep it to one readable line.
7. **Only then**: write the minimum readable code that works.
*Root-cause fix only: grep all callers and resolve issues at the shared root, never patch leaf symptoms.*

## Core Standards & Invariants

1. **DRY & Single Source of Truth (SSOT)**:
   - Absolutely NO duplicate logic. Re-use existing project utilities and abstractions.
   - **Rule of Three**: If logic repeats $\ge 3$ times, extract it to a shared helper or hook immediately.
   - Eliminate duplicated code blocks $\ge 6$ lines across the repository (`python3 scripts/dry_guard.py --check`).

2. **Code Simplification & Flattened Hierarchy**:
   - Eliminate nested conditional pyramids (`if { if { if ... } }`).
   - Use early returns and guard clauses at the top of functions for immediate exit on error or boundary cases.
   - Banish premature abstraction: inline single-use factories, wrappers, and dead variables.
   - Behavioral invariance: simplification must never alter runtime return types or error contracts.

3. **SOLID & Clean Architecture**:
   - **Single Responsibility (SRP)**: Each function and module should have one reason to change.
   - **Dependency Inversion (DIP)**: High-level business logic must not depend directly on low-level I/O.
   - Maintain strict isolation between UI presentation, domain business logic, and infrastructure data access.

4. **Senior Defensive Engineering & Complexity**:
   - Prevent race conditions and resource leaks (clean up event listeners, timers, abort stale HTTP requests).
   - Strict runtime data validation (Zod, Pydantic) on all external inputs and route parameters.
   - Atomic functions with shallow indentation. Default to O(1) dictionary/hash lookups over O(N^2) nested loops.
   - Verify complexity thresholds via `python3 scripts/complexity_analyzer.py`.

5. **Feature Completeness (Anti-Dummy)**:
   - 100% complete production implementations. NO placeholders, mock arrays, or `// TODO` stubs.

## Golden Example: Guard Clause & Early Return
```python
# Bad: Nested Pyramid
def process_order(order):
    if order:
        if order.is_valid():
            if not order.is_paid():
                return charge_card(order)
    return None

# Good: Flattened Early Returns
def process_order(order: Order) -> Result | None:
    if not order or not order.is_valid():
        return None
    if order.is_paid():
        return Result.already_paid(order.id)
    return charge_card(order)
```

## Procedural Workflow
1. **Reconnaissance**: Read sibling files and run `python3 scripts/grounding.py` for project patterns.
2. **Ladder & DRY Check**: Stop at highest rung; check for existing shared utilities.
3. **Refactor In-Place**: Apply guard clauses, inline single-use helpers, and eliminate duplicate logic.
4. **Static Code Audits**:
   - Check duplicate logic: `python3 scripts/dry_guard.py --check`
   - Check function complexity: `python3 scripts/complexity_analyzer.py`
   - Run automated PR review: `python3 scripts/auto_reviewer.py --terse`
5. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **God Functions**: Monster functions handling formatting, validation, database access, and HTTP responses.
- **Copy-Paste Duplication**: Duplicating utility functions across files instead of importing a shared helper.
- **Silent Failure**: Catching exceptions and doing nothing, masking root-cause defects.
