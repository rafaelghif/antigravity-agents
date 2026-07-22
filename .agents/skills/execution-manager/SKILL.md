---
name: execution-manager
description: Oversees tool and dependency invocations to ensure ephemeral execution and prevent redundancy.
---

# Execution Manager Skill

Ensures all agentic operations conform to the Framework-Native Tooling rules defined in AGENTS.md §3.

## When to Execute
- BEFORE installing any new dependency (npm, pip, cargo, etc.).
- BEFORE running any CLI tool or generator script.

## Execution Steps

### 1. Framework Discovery Protocol
Before running any dependency management command, detect the ecosystem:
1. Check for `package.json` -> Use `npm`/`pnpm`/`yarn`.
2. Check for `requirements.txt` -> Use `pip`.
3. Check for `Cargo.toml` -> Use `cargo`.
4. Check for `go.mod` -> Use `go`.
5. Check for `Gemfile` -> Use `bundler`.
*If multiple package managers exist, log a warning and use the most recently modified lock file.*

### 2. Dependency Redundancy Check
1. Identify the core framework being used.
2. Check existing `dependencies` and `devDependencies` to see if a library providing similar functionality is already installed (e.g., `material-ui` vs `bootstrap` vs `tailwind`).
3. If the new dependency provides similar components to an existing library, evaluate if it can be replaced by extending the existing one.
4. Document the reasoning in `.agents/plans/` before executing the installation.

### 3. Ephemeral Invocation Enforcement
- **NEVER** use `npm install -g`, `pip install global`, or any system-wide installation.
- **ALWAYS** use ephemeral executors: `npx`, `pnpm dlx`, `yarn dlx`, or `pipx run`.
