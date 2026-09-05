---
name: devops
description: Use this skill for Docker containers, Kubernetes manifests, CI/CD pipelines, Infrastructure as Code (Terraform), and Model Context Protocol (MCP) server setup.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.45.0"
  category: devops
  tags: [docker, kubernetes, ci-cd, terraform, mcp, security]
---

# DevOps, Cloud Infrastructure & Toolchain Protocol

**Role**: Principal DevSecOps Engineer & Cloud Infrastructure Architect.

## Overview & Trigger Conditions
Activate this skill when configuring Dockerfiles, container orchestrations (Kubernetes), continuous integration/deployment (CI/CD) pipelines, Infrastructure as Code (Terraform/OpenTofu), or Model Context Protocol (MCP) toolchains.

**Trigger Scenarios & Keywords**:
- Containerization, Kubernetes manifests, GitHub Actions, Terraform, MCP configuration.
- Keywords: `docker`, `dockerfile`, `container`, `kubernetes`, `k8s`, `ci/cd`, `terraform`, `iac`, `helm`, `deployment`, `mcp`, `model context protocol`, `mcp server`, `mcp setup`.

## Core Standards & Invariants

1. **Container Hardening (Docker)**:
   - **Multi-Stage Builds**: Separate build-time compilers and SDKs from production runtime artifacts to minimize attack surface.
   - **Non-Root Execution**: Containers must never run as root. Explicitly define an unprivileged user (`USER nonroot` or dedicated UID 10001).
   - **Immutable Base Images**: Use minimal base images (Distroless or Alpine). Pin immutable digests (`@sha256:...`) or exact semantic tags. Mutable `:latest` tags are strictly banned.
   - **Filesystem Hardening**: Mount the root filesystem as read-only (`read_only: true`), mounting writable scratch volumes only to `/tmp` via `tmpfs`.

2. **Kubernetes Architecture & Resilience**:
   - **Ingress Governance**: Enforce the modern Kubernetes Gateway API specification over legacy Ingress controllers.
   - **Strict Resource Boundaries**: Mandate both `requests` and `limits` for CPU and memory on every container to prevent noisy-neighbor evictions.
   - **Lifecycle Probes**: Configure deterministic `livenessProbe` and `readinessProbe` with appropriate `initialDelaySeconds` and failure thresholds for zero-downtime rollouts.

3. **CI/CD Pipelines & Toolchain Governance**:
   - Run pipeline DAGs locally prior to pushing:
     `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml`
   - Automated PR review validation: `python3 scripts/auto_reviewer.py --terse`
   - Continuous Git hygiene & secret scanning: `python3 scripts/git_hygiene_guard.py --check`

4. **Model Context Protocol (MCP) Configuration**:
   - Store configurations in `.agents/mcp_config.json` adhering to the official MCP schema.
   - Inject API credentials exclusively via environment variables (`${API_KEY}`); never hardcode raw secrets.
   - Remote servers must use HTTPS (`serverUrl: https://...`). Mutable `:latest` container args are forbidden.

## Golden Example: Hardened Multi-Stage Dockerfile
```dockerfile
# Stage 1: Build binary
FROM golang:1.23-alpine AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /bin/app .

# Stage 2: Minimal non-root distroless runtime
FROM gcr.io/distroless/static-debian12:nonroot
USER nonroot:nonroot
COPY --from=builder --chown=nonroot:nonroot /bin/app /bin/app
ENTRYPOINT ["/bin/app"]
```

## Procedural Workflow
1. **Infrastructure Audit**: Inspect existing Dockerfiles, CI workflows, and `.agents/mcp_config.json`.
2. **Apply Hardening**: Implement multi-stage builds, non-root users, resource quotas, and secret parameterization.
3. **Pipeline DAG Verification**: Run `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml`.
4. **Git & Secret Scanning**: Run `python3 scripts/git_hygiene_guard.py --check`.
5. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Hardcoded Secrets**: Embedding API tokens or SSH keys in Dockerfile `ENV` instructions or CI YAML files.
- **Root Containers**: Running Node, Python, or Go processes as root (`UID 0`) inside production pods.
- **Unpinned Images**: Relying on `:latest` tags, leading to non-reproducible deployments.
