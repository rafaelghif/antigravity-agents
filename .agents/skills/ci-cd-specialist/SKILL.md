---
name: ci-cd-specialist
description: DevOps and Pipeline management skill to ensure code passes server-side CI/CD environments.
instruction: Use when setting up new CI pipelines, fixing deployment errors, or resolving failed GitHub Actions/GitLab CI runs.
requires_core: ">=4.1.4"
---
# CI/CD Specialist Skill

## Objective
To bridge the gap between local development and server-side execution. Prevents the "It works on my machine" syndrome by rigorously auditing Dockerfiles, CI yaml files, and remote pipeline logs.

## When to Execute
- When a PR check or pipeline fails (e.g., GitHub Actions red cross).
- When modifying `.github/workflows/`, `.gitlab-ci.yml`, or `Dockerfile`.
- When deploying the application to an environment.

## Execution Steps

1. **Pipeline Discovery**:
   - Inspect the `.github/workflows/` or equivalent directory.
   - Understand the runner environment (Ubuntu, Alpine), Node/Python versions, and required environment variables or secrets.

2. **Log Analysis**:
   - When fixing a pipeline failure, DO NOT guess. 
   - Analyze the exact step that failed in the CI/CD log. Identify if the failure is due to a missing dependency, a network timeout, a failing test, or a syntax error.

3. **Local Simulation**:
   - Before committing a fix for a CI issue, attempt to simulate the exact CI command locally if possible (e.g., running `npm run lint` or `docker build` with the exact flags used by the CI).

4. **Security Check**:
   - Ensure that the pipeline does not echo or log secrets.
   - Verify that third-party actions/images use specific commit SHAs (Provenance) rather than mutable tags like `latest` or `v1`.
