# Core Features & Capabilities

This document details the core features and operational capabilities of the Antigravity Agent Core.

---

## 1. Project Initialization & Scaffolding Wizard
If you are starting a project from scratch, running the initialization command launches an interactive prompt wizard that guides you (or the agent) through setting up:
- Project name
- Target language/framework stack (e.g. Node/TypeScript, Go, Python)
- Architectural pattern (e.g. MVC, Clean, Hexagonal)
- Target database / ORM configuration (e.g. Prisma, PostgreSQL, None)
- Required configuration environment variable keys
- Option to automatically scaffold project folders and file templates (e.g. `package.json`, `go.mod`, `main.go`, `main.py`, `.env`)

---

## 2. Autonomous Adaptation Protocol (AAP)
If deployed in an existing codebase, the workspace autodetects the programming language, framework, database migrations, testing commands, and linter configurations. It automatically updates `project_rules.md` and generates relational schema maps inside `schemas/` without manual setup.

---

## 3. Workspace Validator & Security Gate
Ensures strict coding and security practices before code is staged or committed:
- **Secret Scanner**: Detects hardcoded credentials, private keys, passwords, and API keys.
- **Memory Cap Guard**: Keeps `memory.md` under 100 lines for prompt cache hits.
- **Purity Verifier**: Flags raw environment variable reads (e.g., `process.env` or `os.Getenv`) outside config adapters.
- **Automated CI Validation**: Runs validation checks automatically on GitHub pushes and pull requests via the `.github/workflows/antigravity.yml` workflow template.

---

## 4. Native Monorepo Support & Directory-Aware Validation
Antigravity natively supports multi-project repositories (e.g., Turborepo, pnpm workspaces, Yarn workspaces, Go workspaces):
- **Autonomous Discovery**: The recon engine scans the repository and maps out all nested sub-projects under directories like `apps/`, `packages/`, or `services/`.
- **Differential Execution**: Linter and test runners analyze staged git file boundaries, executing commands only on directories that contain modifications, preventing redundant runs and minimizing token consumption.
- **Scaffolding Integration**: The initialization script allows users to scaffold a full Turborepo + pnpm monorepo architecture (Next.js frontend, Go Gin backend API, and shared workspace package) out-of-the-box.

---

## 5. Multi-Agent & Multi-Account Synchronization Protocol
Keeps multiple agents, developers, and distinct user accounts 100% aligned and in sync:
- **Git-Backed Single Source of Truth**: Active task checklists (`memory.md`), project blueprints (`project_rules.md`), design decisions (`adr.md`), and domain schemas (`schema.md`, `schemas/`) are committed and tracked in Git. When a developer or agent pulls modifications (`git pull`), the workspace context aligns instantly.
- **Branch-Aware Upstream Gate**: The validation suite checks if the local repository is behind its remote origin branch. If so, it halts agent execution to prevent code conflicts and split-brain memory states.
- **Sub-Project Module Locks**: Prevents overlapping edits on the same directory by using local locking (`helper.sh lock <path>`). Slash paths are sanitized automatically (e.g., `apps/backend` locks to `apps_backend.lock`).
- **Pre-Merge Checklist Archival**: Clears active memory checklists and archives them to `archive/` upon branch completion to avoid git merge conflicts.

---

## 6. Docker & Local Infrastructure Provisioning
Easily containerize and orchestrate your application components and databases:
- **Dockerfile Generation**: Automatically generates multi-stage, production-ready `Dockerfile` configurations for Next.js, NestJS, Go Gin, FastAPI, and React SPA (served via Nginx).
- **Docker Compose Orchestration**: Configures a unified `docker-compose.yml` to spin up backend services, frontend services, and persistent database volumes.
- **Service Sequencing & Healthchecks**: Automatically structures `depends_on` conditions to ensure application containers wait for database healthchecks (e.g., `pg_isready` for PostgreSQL, `mysqladmin ping` for MySQL, or `redis-cli ping` for Redis) to pass before starting.
- **Port-Clash Prevention**: Intelligently offsets host ports (e.g., mapping host `3001` to frontend `3000`) if backend and frontend containers both default to port `3000`.
