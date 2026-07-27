---
name: quality-assurance
description: Universal Quality Assurance manager for Unit/E2E testing, UI & Accessibility (A11y) auditing, and 5-dimension performance profiling (CPU, I/O, DB, Memory, Network). Triggers during PR reviews, UI component validation, performance profiling, or test suite execution.
requires_core: ">=4.2.0"
---
# Quality Assurance Skill

## Objective
Comprehensive quality assurance covering automated test suites, UI/WCAG accessibility, and multi-dimensional performance profiling.

## 1. Automated Testing (Unit, Integration, E2E)
- Run project test suites (`npm test`, `pytest`, `cargo test`) and ensure 100% pass rate.
- Generate unit/integration tests for uncovered edge cases.

## 2. UI & Accessibility (A11y) Review
- Validate UI components against WCAG 2.1 AA standards (color contrast, semantic HTML, ARIA labels, keyboard navigation).
- Enforce visual aesthetics (Google Fonts, HSL color palettes, dynamic glassmorphism/micro-animations).

## 3. 5-Dimension Performance Profiling
- **Database & Data Access**: Check for N+1 ORM queries and missing indexes.
- **File & Network I/O**: Audit blocking synchronous file reads/writes and API payload compression.
- **CPU & Algorithmic Complexity**: Replace $O(n^2)$ nested loops with $O(1)$ map lookups.
- **Heap Memory & Resource Leaks**: Track memory growth under load; detect listener/handle leaks.
- **Performance Baseline Storage**: Compare metrics against `.agents/brain/perf-baseline.json`. Halt release if performance degrades $>15\%$.
