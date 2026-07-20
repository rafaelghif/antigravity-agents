---
name: devops-release
description: Playbook for CI/CD, release management, comprehensive testing (unit/integration), mocking, security compliance, dependency auditing, and containerization.
---

## Inherited from ci-cd

# CI/CD Pipelines Playbook

This playbook defines best practices, reusable workflows, and optimization strategies for establishing Continuous Integration and Continuous Deployment (CI/CD) pipelines.

---

## 1. Core Execution Phases

Every enterprise CI/CD pipeline should implement the following stages in sequence:

### A. Static Analysis & Linting
- Run syntax checkers, style linters, and static type verifiers (e.g., Flake8, Ruff, ESLint, mypy).
- Fail fast at this stage to prevent expensive test runs on poorly formatted code.

### B. Unit & Integration Testing
- Execute test suites automatically on every commit, pull request, and merge.
- Ensure that the execution runs in a isolated sandbox environment (e.g. docker or virtual environment).

### C. Build & Packaging
- Build production assets, container images, or binaries.
- Ensure builds are deterministic and reproducible.

### D. Security Scanning
- Run SAST (Static Application Security Testing) and dependency auditing tools (e.g., `npm audit`, `pip-audit`, Trivy, Bandit).

---

## 2. Speeding Up Pipelines with Caching

Pipeline execution time directly impacts developer velocity. Always implement dependency caching.

### A. GitHub Actions Caching Patterns
- **Node.js/npm**: Cache `~/.npm` and `node_modules`.
- **Python/pip**: Cache pip download cache and poetry virtual environments.
  ```yaml
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.10'
      cache: 'pip' # built-in pip caching
  ```

---

## 3. Configuration Best Practices

- **Never Commit Secrets**: Never hardcode private keys, passwords, or cloud credentials in pipeline configurations. Always reference secrets from your platform's secure vault (e.g. `${{ secrets.GITHUB_TOKEN }}`).
- **Environment Parity**: Ensure that CI commands can be run locally using a local shell wrapper or script (e.g., `./helper.sh validate` or `npm run test`).
- **Strict Pull Request Gates**: Enforce branch protection rules requiring status checks (linting, tests, build) to pass before a pull request can be merged.

## Inherited from release-management

# Release Management & Deployment Playbook

This playbook establishes the engineering rules for containerizing applications, versioning releases, deploying updates with zero downtime, and verifying post-deployment health.

---

## 1. Enterprise Containerization Best Practices

All dockerized microservices must conform to security and sizing guidelines:

- **Multi-Stage Builds**: Always use multi-stage `Dockerfile` structures to keep final production images tiny and free from compile-time dependencies.
- **Non-Root Execution**: Never run containers as `root`. Always define a custom non-root system user and group (e.g. `USER appuser`).
- **Leverage Build Cache**: Order instructions from least frequently changed (e.g., copying dependencies `package.json`/`requirements.txt`) to most frequently changed (copying source code) to optimize caching.
- **Secure Image Base**: Use minimal, official, and pinned base images (like `python:3.12-slim` or `node:20-alpine`) instead of generic latest tags.

---

## 2. Release Versioning (SemVer)

- **Semantic Versioning Compliance**:
  - **MAJOR**: Incompatible API changes.
  - **MINOR**: Backward-compatible new functionality.
  - **PATCH**: Backward-compatible bug fixes.
- **Auto-Changelog generation**: Always parse git log tags to compile changelogs automatically using the `./helper.sh changelog` command. Never edit changelog releases manually to avoid SemVer mismatches.

---

## 3. Feature Flags & Gradual Rollouts

When releasing high-risk features, decouple deployment from release using feature flags:

- **Flag Wrapping**: Wrap new features in conditional flags:
  ```python
  if feature_flags.is_enabled("new-checkout-flow", user_id):
      return new_checkout_flow()
  else:
      return legacy_checkout_flow()
  ```
- **Gradual Percentages**: Roll out features starting at 1%, then 10%, 50%, and finally 100% to identify regressions early.
- **Flag Cleanups**: Register technical debt issues to clean up and remove the feature flag branching logic once the feature is 100% rolled out.

---

## 4. Deployments & Post-Deployment Smoke Verification

- **Zero-Downtime Deployments**:
  - **Blue-Green**: Maintain two identical environments. Route traffic to the Green environment only after health checks pass.
  - **Canary**: Deploy updates to a tiny fraction of servers, monitor error rates, and promote to the rest of the fleet if stable.
- **Post-Deploy Smoke Tests**:
  - Run lightweight API health check endpoints (`/health` or `/ping`) immediately after deployment.
  - Monitor logs for a spike in 5xx status codes or traceback exceptions. If error rates exceed 1% in the first 5 minutes, trigger an **automated rollback** immediately.

## Inherited from testing

# Testing & Test Automation Playbook

This playbook establishes the guidelines, strategies, and patterns for implementing testing and test automation at an enterprise scale, ensuring code safety, reliability, and zero-regression deployments without unnecessary overhead.

---

## 1. Test Categorization & Isolation

To maintain a fast and reliable CI/CD pipeline, tests are divided into two tiers (E2E testing is omitted to optimize token usage and avoid redundant runtime overhead):

### A. Unit Tests (Fast & Deterministic)
- **Scope**: Validate single functions, utility modules, or isolated classes.
- **Rules**:
  - Must run completely offline (no database, no external network, no file system read/write dependencies).
  - Use mocking or dependency injection to isolate the code under test.
  - Execution speed must be under 100ms per test.

### B. Integration Tests (Component Interoperability)
- **Scope**: Validate interactions between modules, database repositories, API clients, and services.
- **Rules**:
  - Network and database components may be active, but should preferably use local mocks or isolated databases (e.g., SQLite in-memory).
  - Maintain absolute cleanup (rollback database transactions or reset state) after each test run.

---

## 2. Mocking Guidelines & Best Practices

Mocking is essential for isolation, but over-mocking leads to fragile tests that fail to detect real integration bugs.

### A. What to Mock
- **External APIs**: Always mock HTTP calls to external vendors or web endpoints.
- **Timers and System Clocks**: Mock time dependencies to ensure consistency (e.g., testing token expiration).
- **Expensive Operations**: Mock heavy computational tasks or slow subprocesses.

### B. Mocking Patterns in Python (pytest / unittest.mock)
```python
from unittest.mock import patch, MagicMock

# Best Practice: Patch at the import location, not definition location
@patch('module_under_test.external_api_call')
def test_fetch_user_data(mock_api):
    # Setup mock return value
    mock_api.return_value = {"id": 1, "name": "John Doe"}
    
    result = module_under_test.get_user(1)
    
    assert result["name"] == "John Doe"
    mock_api.assert_called_once_with(1)
```

---

## 3. Test Organization & Conventions

To keep tests clean and maintainable:
- **Test Directory**: Place all tests in a `tests/` directory at the root of the project.
- **File Naming**: Name files with a `test_` prefix (e.g., `test_auth.py`, `test_utils.py`).
- **Test Cases**: Name test functions descriptively starting with `test_` followed by the action and expected behavior (e.g., `test_authenticate_with_invalid_credentials_fails`).
- **Assertive Assertions**: Use specific assertions and descriptive error messages rather than simple `assert True`.

---

## 4. The Test-Driven Development (TDD) Cycle
- **Red**: Write a failing unit test that describes the desired feature or bugfix *before* writing any production code.
- **Green**: Write the minimal amount of code necessary to make the test pass.
- **Refactor**: Clean up the implementation. Remove duplication, improve naming, reduce cognitive complexity, and ensure type safety.

## Inherited from security-compliance

# Security & Compliance Playbook

This playbook outlines steps for auditing code changes against security guidelines, secret exposure risks, and library vulnerabilities, as well as managing dependencies.

## 1. Secrets Leak Prevention
- **Scan Working Tree**: Search for hardcoded keys, passwords, bearer tokens, AWS IDs, or RSA keys before staging changes.
- **Gitignore Verification**: Ensure `.env` and other local credentials files are explicitly ignored in `.gitignore`.
- **Environment Templates**: Always document required environment variables in a generic template file (e.g. `.env.example`) containing placeholders rather than values.

## 2. Vulnerability Assessment Checklist
- **SQL Injections**: Check all database operations. Ensure queries use parameterized inputs or ORM safe-execution methods. Never concatenate raw strings inside database queries.
- **XSS (Cross-Site Scripting)**: Verify that user inputs are sanitized and escaped before rendering them in HTML or sending them to client applications.
- **Static Analysis (SAST)**: Use automated static code security scanners (e.g., `bandit` for Python, `eslint-plugin-security` for JavaScript/TypeScript, or CodeQL) to scan the codebase for structural vulnerabilities.
- **Insecure Dependencies**: Run dependency vulnerability scans:
  - For Node.js: `npm audit` or `pnpm audit`
  - For Python: `pip-audit` or `safety check`
  - For Go: `govulncheck ./...`

## 3. Deployment Security
- **Least Privilege**: Ensure network egress rules and API scopes are restricted to the bare minimum required for operations.
- **Secure Storage**: Sensitive configuration files or API keys MUST NOT be globally stored in `~/.` or shared user folders on servers.

## 4. Package Auditing & Compliance
- **Package Pinning**: All dependencies in production applications MUST be pinned to exact versions (e.g. `1.2.3` instead of `^1.2.3` or `*`). This ensures reproducible builds and protects against supply chain attacks.
- **License Auditing**: Verify that third-party packages do not use restrictive copyleft licenses (like GPL) if the project is proprietary. Stick to MIT, Apache 2.0, or BSD licenses when possible.
- **Upgrade Verification**: When upgrading packages, always check the package's changelog for breaking changes and run the full test suite immediately.
- **Package Pruning**: Regularly scan for and remove unused dependencies from `package.json` or `requirements.txt` to minimize the attack surface.