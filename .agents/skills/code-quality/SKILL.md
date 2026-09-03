---
name: code-quality
description: Use this skill when writing, refactoring, or reviewing code to ensure SOLID principles, clean architecture, DRY deduplication, and anti-overengineering simplification.
---

# Code Quality & Simplification Protocol

<CRITICAL_DIRECTIVE>
Enforce Staff-level procedural rigor, the Senior Ladder, DRY deduplication, and pragmatic code simplification.
"Clarity over cleverness. Code is read 10x more often than it is written. The best code is the code never written."
</CRITICAL_DIRECTIVE>

<THE_SENIOR_LADDER>
Before writing code, stop at the first rung that holds:
1. **Does this need to exist?** -> Skip it (YAGNI).
2. **Already in codebase?** -> Reuse existing helper/hook/type/component.
3. **Stdlib does it?** -> Use standard library.
4. **Native platform feature?** -> Native HTML5/CSS/DB constraint over heavy libraries.
5. **Existing dependency?** -> Use installed libraries; never add new dependencies for trivial tasks.
6. **Can it be one line?** -> One line.
7. **Only then:** write the minimum code that works.
*Root-cause fix only: grep all callers and fix at the shared root, never patch leaf symptoms.*
</THE_SENIOR_LADDER>

<ENTERPRISE_STANDARDS>
1. **DRY & Single Source of Truth (SSOT)**:
   - Absolutely NO duplicate logic. Re-use existing project utilities and components.
   - **Rule of Three**: If logic repeats >= 2 times, extract it to a shared helper or hook immediately.
   - Scan duplicates via `python3 scripts/dry_guard.py --check`.
2. **Code Simplification & Flattened Hierarchy**:
   - Eliminate arrow-nested conditional pyramids (`if { if { if ... } }`).
   - Use early returns and guard clauses at the top of functions for immediate exit.
   - Banish premature abstraction: inline single-use factories, wrappers, and dead variables.
   - Behavioral invariance: simplification must never alter runtime return types or error contracts.
3. **SOLID & Clean Architecture**:
   - Single Responsibility (SRP) and Dependency Inversion (DIP).
   - Strict isolation between UI presentation, domain business logic, and infrastructure/data access.
4. **Senior Defensive Engineering**:
   - Prevent race conditions and memory leaks (clean up event listeners, timers, abort stale requests).
   - Strict runtime data validation (Zod, Pydantic) on all external inputs and route parameters.
   - Comprehensive error boundaries with structured domain errors (no silent `except: pass` or `any` types).
5. **Cyclomatic Complexity & Algorithmic Supremacy**:
   - Atomic functions with shallow indentation. Default to O(1) hash lookups over O(N^2) nested loops.
6. **Feature Completeness (Anti-Dummy)**:
   - 100% complete production implementations. NO placeholders, mock arrays, or `// TODO` stubs.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Reconnaissance**: Read sibling files and run `python3 scripts/grounding.py` for project patterns.
2. **Ladder & DRY Check**: Stop at the highest rung; check for existing shared functions.
3. **Refactor In-Place**: Apply guard clauses, inline single-use helpers, and eliminate duplicate logic.
4. **Local Verification**: Run `python3 scripts/verify.py --execute` to guarantee 100% behavioral equivalence.
5. **Assert Zero Clones**: Run `python3 scripts/dry_guard.py --check` before completing the task.
</PROCEDURAL_WORKFLOW>
