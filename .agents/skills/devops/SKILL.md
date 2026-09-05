---
name: devops
description: Use this skill for Docker containers, Kubernetes manifests, CI/CD pipelines, Infrastructure as Code (Terraform), and Model Context Protocol (MCP) server setup.
---

# Enterprise DevOps, Infrastructure & Toolchain Protocol

<CRITICAL_DIRECTIVE>
Enforce zero-downtime deployments, immutable container security, least-privilege infrastructure, and deterministic MCP toolchain configuration.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Containerization (Docker)**:
   - Always use multi-stage builds to minimize image size and attack surface.
   - Never run containers as `root`. Specify `USER nonroot` explicitly.
   - Use distroless or alpine base images for production deployments.
2. **Kubernetes Architecture**:
   - Enforce the Gateway API standard instead of legacy Ingress controllers.
   - Mandate strict Resource Quotas (Requests & Limits) on all deployment manifests.
   - Configure Readiness and Liveness Probes to guarantee zero-downtime rolling updates.
3. **Infrastructure as Code (Terraform / OpenTofu)**:
   - Remote encrypted state storage with distributed state locking (e.g. S3 + DynamoDB).
   - Enforce Policy-as-Code (Checkov, OPA) to prevent misconfigurations from going live.
4. **CI/CD Pipelines & Supply Chain Security**:
   - Enforce protected branches and automated verification gates before merge.
   - Execute CI/CD pipeline stages locally via `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml`.
   - Submit or inspect automated PR reviews via `python3 scripts/auto_reviewer.py` (`--pr <num> --submit`).
   - Enforce clean git branch state and zero secret leaks via `python3 scripts/git_hygiene_guard.py --check`.
   - Generate Software Bill of Materials (SBOM) and container image provenance signing.
5. **Model Context Protocol (MCP) Toolchain Configuration**:
   - Store configurations in `.agents/mcp_config.json` adhering to the official MCP JSON schema.
   - Security First: NEVER hardcode raw API tokens in tracked files. Inject secrets exclusively via environment variables.
   - Least Privilege: Expose only the required database schemas, read scopes, or tools.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Inspect Infrastructure**: Check existing Dockerfiles, CI workflows, and MCP configurations.
2. **Apply Hardened Manifests**: Implement multi-stage builds, non-root users, and secret parameterization.
3. **Verify Compliance & Pipelines**: Run `python3 scripts/git_hygiene_guard.py --check`, `python3 scripts/dag_orchestrator.py .agents/workflows/standard_pr.yaml`, and `python3 scripts/verify.py --execute`.
</PROCEDURAL_WORKFLOW>
