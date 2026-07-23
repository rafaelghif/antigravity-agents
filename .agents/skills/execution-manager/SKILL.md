---
name: execution-manager
description: Tool and dependency invocation oversight, ephemeral execution manager.
instruction: Use before installing dependencies, running generators, or executing tools (npm, pip) to ensure ephemeral execution.
requires_core: ">=4.0.0"
---

# Execution Manager Skill

Ensures all agentic operations conform to the Framework-Native Tooling rules defined in AGENTS.md.

## When to Execute
- BEFORE installing any new dependency (npm, pip, cargo, etc.).
- BEFORE running any CLI tool or generator script.

## Execution Steps

### 1. Framework Discovery Protocol
Before running any dependency management command, detect the ecosystem using the shared **Framework Detection** logic in `.agents/common/utils.md`. Document reasoning in `.agents/plans/dependency-<date>.md` if multiple exist.

### 2. Dependency Redundancy Check
1. Identify the core framework being used.
2. Check existing `dependencies` and `devDependencies` to see if a library providing similar functionality is already installed (e.g., `material-ui` vs `bootstrap` vs `tailwind`).
3. If the new dependency provides similar components to an existing library, evaluate if it can be replaced by extending the existing one.
4. Document the reasoning in `.agents/plans/` before executing the installation.

### 3. Ephemeral Invocation & Supply Chain Security
- **NEVER** use `npm install -g`, `pip install global`, or any system-wide installation.
- **ALWAYS** use ephemeral executors: `npx`, `pnpm dlx`, `yarn dlx`, or `pipx run`.
- **Version Pinning**: Prefer `npx -y <package>@<version>` over `npx <package>`. Check for `@latest` and warn if used. Document installed version in `.agents/scratch/deps.log`.
- **Security**: Use `npm audit` or `safety check` before installation. Block if high‑severity vulnerabilities exist. Verify trust metrics against `.agents/config.json`. Document reasoning for any package with < 10k weekly downloads.

### 4. API Version Negotiation
- Before invoking external tools (e.g., Gitea, GitHub, MCP), verify version compatibility (see `.agents/common/utils.md`).
- Fallback to safe known API endpoints if the newest API version is unsupported.
