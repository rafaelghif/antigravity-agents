---
name: code-quality
description: Use this skill when the user asks to write, refactor, or review application code to ensure enterprise-grade maintainability.
---

<CRITICAL_DIRECTIVE>
Enforce Staff-level procedural rigor and Enterprise-Grade software architecture during implementation.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **DRY & Single Source of Truth (SSOT)**: Absolutely NO duplicate logic. Re-use existing project hooks, utilities, and components. If logic repeats >= 2 times, extract it to a shared module immediately.
2. **Project Pattern Harmony**: NEVER introduce pattern schizophrenia. Before coding, inspect existing sibling files. Strictly adhere to the project's established conventions for state management, data-fetching, error handling, directory structure, and styling.
3. **SOLID & Clean Architecture**: Enforce Single Responsibility (SRP) and Dependency Inversion (DIP). Maintain strict isolation between UI presentation, domain business logic, and infrastructure/data access.
4. **Senior Defensive Engineering**: 
   - Prevent race conditions and memory leaks (clean up event listeners, timers, abort stale requests with AbortController).
   - Strict runtime data validation (Zod, Pydantic) on all external inputs, APIs, and route params.
   - Comprehensive error boundaries with structured domain errors (no silent failures or ad-hoc console.log).
5. **Cyclomatic Complexity & Algorithmic Supremacy**: Keep functions atomic with shallow indentation. Default to O(1) lookups instead of O(N^2) loops. Memoize expensive operations.
6. **Zero-Tolerance Anti-Patterns**: NO `any` types in TypeScript. NO broad `except Exception:` blocks in Python. NO inline CSS styles or ad-hoc duplicate UI primitives.
7. **Feature Completeness (Anti-Dummy)**: 100% complete production implementations. NO placeholders, mock arrays, or `// TODO` stubs. Handle loading, empty, and error states gracefully.
8. **Security & Secrets**: All credentials, tokens, and sensitive configs MUST come from environment variables.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Pattern Reconnaissance**: Search and read existing sibling files to identify established project patterns (state, API, styling, error handling).
2. **Reuse Audit**: Check for existing shared components, hooks, or utilities before creating new ones to maintain DRY.
3. **Context Acquisition**: Understand imports, contracts, and type definitions before modifying code.
4. **Minimal Delta Enforcement**: Implement ONLY the requested feature with maximum architectural elegance.
5. **Test Gap Analysis & TDD**: Ensure tests exist and cover all edge cases before modifying implementation.
6. **Local Verification**: Run stack linter, typecheck, and test runner via `python3 scripts/verify.py --execute`.
7. **Diff Review**: Verify zero duplicate code, zero pattern deviations, and complete feature coverage.
</PROCEDURAL_WORKFLOW>
