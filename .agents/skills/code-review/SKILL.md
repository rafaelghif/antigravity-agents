---
name: code-review
description: Audits production code modifications for type cleanliness, security, architectural boundaries, Swagger documentation, and unit test compliance.
---

# Code Review & Quality Gate Skill

## 1. Input Specification
- **Modified Diffs**: Git diff list of staged or modified files.
- **Project Blueprints**: Config schemas, API docs specifications, and architectural rules.

## 2. Operational Procedures
1. **Source Code Auditing (Diff Check)**:
   - Run line-by-line checks on modified blocks to ensure:
     - No debugging remnants are left (`console.log`, `print`, `debugger`, raw print statements).
     - No hardcoded access credentials, passwords, or S3 key strings.
     - Comments are clean, professional, and explain non-obvious code paths.
2. **Type Safety & Cleanliness Audit**:
   - Verify that no type bypass methods are used (e.g. `any` in TypeScript, raw interface{} in Go, untyped variables where strict types are available).
   - Ensure all type casting is safe, and edge cases are handled (e.g. avoiding unchecked null/undefined property lookups).
3. **Architectural Boundary Gate**:
   - Check if database operations, frameworks, or security packages bleed into business use cases or core domain entities.
   - For web apps: Check if presenter UI components import network client classes (Axios, Fetch) directly instead of utilizing service wrappers or React Query adapters.
4. **Contract and API Docs Compliance**:
   - Confirm that DTOs utilize correct validation rules.
   - Confirm that API endpoints are decorated with clear descriptions, route mappings, and explicit return type schemas.
5. **Testing & Coverage Audit**:
   - Verify that test suites cover all newly added or modified methods.
   - Ensure mocks correctly isolate tests from running local databases or calling external third-party services.
   - Confirm global unit tests pass with zero failures.

## 3. Decision Matrix
- **Is there a type bypass or lint warning?**
  - **YES**: Stop the review. Reject the check. Instruct the agent/developer to declare strict interfaces or union types, and resolve lints.
- **Does the code bleed across boundaries?**
  - **YES**: Reject. Instruct to refactor using service/repository wrappers to keep layers decoupled.
- **Does it pass all checks and verification suites?**
  - **YES**: Accept. Approve the commit/PR.

## 4. Error Mitigation Tree
- **Global test suite fails during pre-commit checks**:
  - *Mitigation*: Identify the broken tests from console logs. If the error is due to changed mock inputs, update the specs. If it's a regression bug, revert the code change, diagnose, and fix.

## 5. Output Verification Gate
- [ ] Staged code compiles clean with no warnings/errors.
- [ ] Secrets and credential configurations are fully isolated.
- [ ] Newly added lines satisfy target code coverage limits.
- [ ] PR Review Handover document generated.
