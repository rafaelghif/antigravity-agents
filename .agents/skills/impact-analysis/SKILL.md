---
name: impact-analysis
description: Audits the long-term architectural, performance, security, and maintainability impacts of any feature design or code mutation.
---

# Long-Term Impact & Dependency Analysis Skill

## 1. Input Specification
- **Proposed Mutation/Feature**: Description of the changes to be made.
- **Affected Domain/Modules**: List of files, databases, routes, or interfaces that interact with the modified sections.
- **Project Lifespan Context**: Designing with a long-term (up to 10-year) maintainability and scalability horizon.

## 2. Operational Procedures
1. **Critical Thinking Assessment**:
   - Before writing any code, write down a mental or scratchpad analysis of the proposed implementation path.
   - Run a multi-dimensional analysis on:
     - **Architectural Coupling**: Ensure zero leakages. Core business domains must remain completely framework-agnostic.
     - **Performance & Resource Scalability**: Analyze database query count (avoid N+1), index usages, network roundtrips, and memory consumption.
     - **Security & Data Privacy**: Check inputs for injection, cross-site scripting, rate-limiting violations, data access authorization, and credential leakages.
     - **Backward Compatibility**: Verify that existing clients, APIs, or database records are not broken.
     - **10-Year Maintainability**: Avoid convoluted patterns, unchecked external dependencies, or unverified imports. Write clean, self-documenting code.
2. **Structural Dependency Mapping**:
   - Scan downstream dependencies of any file being modified using `grep_search` or code analysis to trace what else might break.
3. **Interactive Validation Gate**:
   - If any potential high-risk impact is detected (e.g., database schema changes, backward-incompatible API changes, high latency operations, or major security risks), the agent MUST halt execution and consult the user using a clear multiple-choice list of alternatives before proceeding.

## 3. Decision Matrix
- **Does the task involve changing database columns or relational constraints?**
  - **YES**: Write a migration plan, check database compatibility, and ask the user for approval.
- **Does the task introduce a new third-party package?**
  - **YES**: Analyze the package's security posture, active maintainer status, bundle size, and license compliance before importing.
- **Does the code bleed boundary layers (e.g., ORM annotations in domain structs, HTTP logic in services)?**
  - **YES**: Refactor to introduce proper abstraction layers (like Repository patterns or interfaces).

## 4. Output Protocol
For all major features or architectural shifts, record the design choices and downstream analysis under a new Architectural Decision Record (ADR) in `.agents/adr.md` or a workflows folder before writing code.
