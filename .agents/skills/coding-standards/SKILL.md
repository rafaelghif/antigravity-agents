---
name: coding-standards
description: Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity.
---

# Coding Standards & Practices Playbook

This playbook establishes the professional engineering standards required for writing, reviewing, testing, and designing software at an enterprise level.

---

## 1. Pre-Implementation Impact Analysis Protocol

Before writing any code or proposing design decisions, the agent MUST perform a comprehensive Impact Analysis. This critical thinking phase must be documented in the issue specification or shared directly with the user.

### Analysis Structure
1. **Explore Options**: Propose at least two different implementation approaches (e.g. Option A vs Option B).
2. **Trade-offs Matrix**: Compare options on complexity, maintainability, dependency footprints, performance, and UI/UX ease-of-use.
3. **Downstream Impacts**: Evaluate how each option affects other parts of the workspace, future compatibility, prompt cache size, and developer cognitive load.
4. **Recommendation**: Clearly state the recommended approach and justify why it offers the best balance of robustness and UX/DX simplicity.

---

## 2. The Code Writer Playbook (Writing High-Quality Code)

A world-class code writer transforms ambiguous problems into clean, robust, and self-documenting code.

### A. The TDD (Test-Driven Development) Cycle
- **Red**: Write a failing unit test that describes the desired feature or bugfix before writing any production code.
- **Green**: Write the minimal amount of code necessary to make the test pass.
- **Refactor**: Clean up the implementation. Remove duplication, improve naming, reduce cognitive complexity, and ensure type safety.

### B. Defeating Cognitive Complexity
- **Short Functions**: Keep functions under 50 lines. If a function does more than one thing, split it.
- **Guard Clauses**: Return early to eliminate nested `if-else` blocks and reduce indentation levels.
- **Descriptive Naming**: Use clear, pronoun-free naming for variables, classes, and methods.

### C. Defensive Code Design
- **Input Validation**: Check arguments at API boundaries for type safety, ranges, and nullability.
- **Safe Resource Lifecycle**: Always use context managers (`with` statements in Python) for open files, database connections, and sockets.

### D. Strict Type Hints & Annotations
- **Required Types**: Every function/method signature MUST declare parameter types and return types (e.g., `def calculate_sum(a: int, b: int) -> int:`).
- **Avoid Generic Fallbacks**: Avoid using generic `Any` type annotations unless absolutely necessary. When generics are needed, use type variables (`TypeVar`) or Union/Optional types for precision.
- **Static Type Checkers**: Run local checkers (e.g., `mypy` or `tsc`) to verify type compliance before commits.

---

## 3. The Code Review Playbook (Zero-Regression Inspections)

A world-class code reviewer ensures code quality, correctness, and team consistency prior to merges.

### A. The Self-Review (First Line of Defense)
Before proposing any code review, developers must self-review their changes:
- **Diff Inspection**: Examine `git diff` line-by-line to ensure no debug/temporary code or logging statements are left.
- **Code Documentation**: Verify all public APIs have clean docstrings explaining parameters, returns, and exceptions.

### B. Core Inspection Gates
- **Secrets Audit**: Programmatically and visually verify that no credentials, API keys, passwords, or `.env` configurations are checked in.
- **Insulation Check**: Verify that layer boundaries are maintained. Helper utilities, DB models, and third-party frameworks must not bleed into core business logic.
- **DRY & SOLID Verification**: Identify duplicate code patterns and recommend modular class structures following SOLID principles.
- **Type Safety**: Ensure no variable types are declared as generic `Any` or left untyped at public interface boundaries.

### C. Common Code Smells to Reject
- **Dead Code**: Unused imports, variables, functions, or commented-out code blocks.
- **Magic Strings/Numbers**: Replace inline literals with named constants or configuration variables.
- **Swallowed Exceptions**: Reject try-except blocks that catch general exceptions without logging or raising them.

---

## 4. Testing & Validation Gates

Quality is not verified after implementation—it is built-in.

- **Deterministic Tests**: Mock all network APIs, database queries, and OS processes. Unit tests must run offline, deterministically, and fast (under 100ms per test).
- **Edge Case Coverage**: Write test assertions for null inputs, boundary values, empty arrays, and error-throwing states.
- **Automated Validation**: Ensure static linting, typing checks, and testing suites are run before staging commits.

---

## 5. Architectural Integrity & Design Decisions (ADRs)

Maintain a long-term, self-documenting system architecture.

- **Use ADRs**: For every major design choice (e.g. library addition, folder reorganization, protocol switch), write an Architectural Decision Record in `.agents/memory/decisions/`.
- **Decoupled Architecture**: Structure modules into clear domains with well-defined APIs. Keep system utilities separate from business logic.

---

## 6. Token & Context Efficiency Playbook

To optimize agent runtime cost, token consumption, and cognitive footprint, agents must strictly follow these rules:

- **Targeted File Reads**: Avoid viewing whole files. Always specify `StartLine` and `EndLine` parameters when calling `view_file` to target only the code relevant to the task.
- **Decoupled Subagents**: Only invoke subagents for separate, heavy, or multi-step research operations. Perform straightforward code editing and validation within the parent agent context.
- **Zero Redundant Commands**: Do not run repetitive commands or searches. If a search query or validation command fails 3 times, immediately halt and prompt the user.
- **No E2E testing overhead**: Do not request, setup, or run browser-based End-to-End or UI tests unless explicitly demanded by the user. Focus strictly on fast, mock-driven unit and integration testing.
