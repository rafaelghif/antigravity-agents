---
name: ci-cd
description: Playbook for setting up CI/CD pipelines, automating linting, testing, building, caching, and staging release gates.
---

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
