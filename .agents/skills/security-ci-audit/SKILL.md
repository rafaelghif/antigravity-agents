---
name: security-ci-audit
description: Verifies security configurations, scans for hardcoded credentials, checks CORS/rate-limiting setup, API docs compliance, and environment schema validation.
---

# Security & CI Compliance Audit Skill

## 1. Input Specification
- **Modified Source Code**: List of added or changed files in the active commit stack.
- **Project Configuration**: Environment validation files, API gateway bootstrap files, security middlewares.

## 2. Operational Procedures & Checklist
1. **Secret Scanning Pattern Match**:
   - Run grep pattern searches to identify hardcoded credentials:
     - Private key block indicators (e.g., `-----BEGIN PRIVATE KEY-----`).
     - Files with credentials (e.g., `credential*.json`, `key*.json`, `.pem`).
     - Hardcoded password strings or credentials: `api_key`, `secret`, `password` assignments.
2. **Environment Variable Validation Audit**:
   - Scan the codebase for raw environment variable reads (e.g. `process.env` in JS/TS, `os.Getenv` in Go, `os.environ` in Python).
   - Verify that all environment configs are validated at application bootstrap using a schema validator or config loading service, avoiding raw access scattered across domain layers.
3. **API Documentation Audit**:
   - For all files modified under API boundary folders (e.g., controllers, handlers):
     - Verify properties and endpoints are documented with clear tags, JSDoc/Swagger comments, or annotations.
     - Verify response schemas and return status codes are explicitly declared.
4. **Domain Layer Purity Audit**:
   - Verify files inside core business domain layers have zero dependencies on frameworks, HTTP routers, or ORM annotations.
5. **Third-Party Isolation Audit (Frontend UI)**:
   - Verify UI components consume abstract client/adapter interfaces (e.g., wrapper hooks or service adapters) rather than importing raw HTTP clients or native device packages directly.
6. **Observability and Security Middleware Audit**:
   - Verify that the API gateway entrypoint initializes:
     - Security headers (e.g., Helmet, CORS rules restricting wildcards).
     - Global validation pipelines for incoming requests.
     - Rate-limiting (throttling) policies.
     - Dependency health check endpoints (checking database, cache, storage connectivity).

## 3. Decision Matrix
- **Was a raw environment variable access violation found?**
   - **YES**: Replace the raw access with the appropriate property retrieved from the config loading service, and register the new key in the schema loader if not already mapped.
- **Did a route handler miss API docs annotations?**
   - **YES**: Add the appropriate annotations or documentation blocks to ensure schema contract compliance.

## 4. Error Mitigation Tree
- **App fails to boot due to env validation errors**:
   - *Mitigation*: Inspect the validation logs. Copy missing parameters from the configuration example into your local `.env`, bind the correct value type, and re-run startup.

## 5. Output Verification Gate
- [ ] No private keys or credentials files are tracked in git.
- [ ] Direct environment variables access is strictly restricted to the configuration module.
- [ ] API endpoints and models explicitly declare return types and validation rules.
- [ ] Health Check endpoint tracks active services.
- [ ] Rate limiting and security headers are initialized at the gateway.
