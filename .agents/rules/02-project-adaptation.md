---
name: project-adaptation
description: Target project convention compliance, existing code reuse, and minimal change principle.
trigger: always_on
---

# Target Project Standards & Code Reuse

- **Project Standard Has Priority**: Follow the target repository's architectural patterns, module boundaries, idioms, and naming conventions. Existing Project > General Best Practice > Personal Preference.
- **Reuse Before Creating**: Preferred order: EXISTING COMPONENT -> EXISTING UTILITY -> EXISTING ABSTRACTION -> MINIMAL MODIFICATION -> NEW IMPLEMENTATION ONLY IF NECESSARY. Never create duplicate abstractions or copy-paste code.
- **Minimal Delta**: Make the smallest correct change that solves the issue. Unrelated refactoring, reformatting, or style migrations are strictly prohibited.
- **Dependency Discipline**: Never introduce external dependencies unless strictly necessary and verified compatible across target OS (Linux/macOS/Windows) and runtimes.
