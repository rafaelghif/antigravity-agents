---
name: devops-release
description: Playbook for setting up CI/CD pipelines, automating linting, testing, building, caching, and staging release gates. Guidelines for containerization (Dockerfile best practices), release versioning, blue-green deployment, feature flag rollouts, and post-deployment smoke verification.
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