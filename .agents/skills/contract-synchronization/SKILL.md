---
name: contract-synchronization
description: Playbook for managing API contract schemas, generating client code, and verifying backend/frontend synchronization.
---

# API Contract & Multi-Project Synchronization Playbook

This playbook defines the standards and workflows for maintaining absolute contract compliance and synchronization between backend and frontend sub-projects in a monorepo workspace.

---

## 1. Shared Schema: The Single Source of Truth

To prevent API contract mismatch and runtime integration errors:
- **Define a Contract**: Place a machine-readable API specification (e.g., `openapi.yaml`, `schema.json`, or shared Type Definitions) in a shared directory at the root of the workspace or in the backend's public docs directory (e.g., `docs/openapi.yaml`).
- **Never Define Types Manually**: The frontend must not manually recreate request/response interfaces or endpoint routes. All API-related types, endpoints, and HTTP client bindings must be derived from the shared schema.

---

## 2. Automated Frontend Client Codegen

To synchronize changes instantly from Backend $\rightarrow$ Frontend:
- **Codegen Trigger**: When backend API models are modified, run the client code generator (e.g. `openapi-generator-cli`, `orval`, or custom typescript generators) to regenerate types and fetching hooks inside the frontend directory (e.g. `app/frontend/src/api/`).
- **Check-in Policy**: Generated client files MUST be checked into source control along with the API contract modification. The build pipeline will fail if the code generator produces unstaged changes.

---

## 3. Double-Sided Contract Verification

Validation must happen on both ends of the interface boundary:

### A. Backend-Side Verification
- Validate that the actual endpoints match the declared API specification.
- Use schema-driven test runners (e.g., **Schemathesis** in Python, or **openapi-validator** in Node.js) to dynamically fuzz or test backend routes against the OpenAPI file:
  ```bash
  schemathesis run docs/openapi.yaml --base-url http://localhost:8000/api
  ```

### B. Frontend-Side Verification
- Ensure the frontend build process strictly compiles against the generated TypeScript definitions.
- Running `npm run build` or `tsc --noEmit` in the frontend directory serves as the final gate to verify that all API components, arguments, and data shapes match the backend payload.

---

## 4. Multi-Project Validation Gate

When validation is run, the agent must check all projects. The root validation script [validate.py](file://./.agents/scripts/validate.py) reads [.agents/projects.json](file://./.agents/projects.json) to automatically run tests in each sub-directory (e.g., `app/backend` and `app/frontend`), ensuring that changes in one module do not break the tests in the other.
