# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.

---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: [e.g. Node/TypeScript, Python/FastAPI, Go, Rust]
- **Directory Structure**:
  - `src/` -> Application source code
  - `tests/` -> Test suites

## 2. Architectural Conventions
- [Describe the architecture pattern here, e.g. Clean Architecture, MVC, Hexagonal, simple service-repository layer]
- [Define rules regarding coupling and boundaries, e.g. UI layers must not call database adapters directly]

## 3. Spacing & Styling Standards
- [Define layout spacing, form guidelines, or styling patterns if frontend project, or code style rules]

## 4. Security & External Services
- [Define database transaction rules, third-party adapters (S3, Auth, Payment), and caching protocols]

## 5. Long-Term Impact & 10-Year Maintainability Gates
- **Impact-Analysis Check**: Before installing new packages, modifying database structures, or altering cross-domain APIs, the agent must run the `impact-analysis` skill and document design rationales.
- **Architectural Boundary Gate**: Domain business logic must remain completely independent of libraries and frameworks (e.g. database schemas, server frameworks).
- **Code Sustainability**: Code must prioritize long-term readability over brevity. Avoid complex runtime assumptions, unverified imports, or undocumented configuration requirements.
- **Ambiguity Gate**: If any implementation details are unclear, halt and ask the user for confirmation first.
