# AGENTS.md — Antigravity Agent Core (AAC) V4

This core directive governs all agents in this workspace.

## 1. Core Principles & Autonomy
- **Proactive Execution**: Operate autonomously. Use the `ask_question` tool for critical decisions (schema changes, new dependencies, auth changes, data deletion, modifying `.agents/`). If a 5-minute timeout occurs waiting for user input, stop any active Gitea time trackers, log to `.agents/incidents/`, notify the user via `ask_question` that the operation was aborted due to timeout, and abort safely. Use the separate `ask_permission` tool *strictly* for OS-level permission errors (EACCES, EPERM). If both apply, `ask_question` wins.
- **Tenacity vs. Escalation (Rollback Protocol)**: Iteratively explore solutions. If 3 distinct approaches fail, trigger the Rollback Protocol: (1) Snapshot failed state (`git stash`), (2) Document incident in `.agents/incidents/<slug>-<date>-incident.md` (Severity, Impact, Context, Approaches, Root Cause, Reverted To), (3) Revert to last known good state, (4) Validate state (run linters, unit tests, smoke tests). If validation fails, revert to the exact commit before the branch was created, and escalate to the user with the validation failures.
- **Rule Precedence**: The rules in this `AGENTS.md` file are the supreme constitution. If a `.agents/skills/<name>/SKILL.md` conflicts with this document, `AGENTS.md` ALWAYS wins. Any skill that diverges from this directive is considered invalid and must be corrected.
- **Unified Planning**: Complex tasks require sequential planning: (1) Unless bypassed by `!quick`, create a GitHub/Gitea issue for external tracking, then (2) Create a lightweight task checklist in `.agents/plans/` for internal traceability.

## 2. Anti-Hallucination & State Management
- **Zero-Assumption Policy**: NEVER guess file contents, variables, database schemas, or API props. Verify via `grep_search`, `view_file`, or documentation.
- **Strict Schema Documentation**: Document all database/architecture contracts in `.agents/brain/schema.md`. Any schema mutation demands a global cascading impact analysis.
- **Directory Manifest**: Store all artifacts strictly within these designated workspace locations:
  - `.agents/scratch/`: Ephemeral/short-term notes, debugging context.
  - `.agents/brain/`: Permanent decisions, `schema.md`, architectural records.
  - `.agents/incidents/`: Post-mortem incident reports for failed tasks.
  - `.agents/plans/`: Lightweight sequential task checklists.
  - `.agents/skills/`: Auto-generated, reusable operational skills.
- **Token Optimization & Verification**: Aggressively limit context window size. Use `StartLine`/`EndLine`. A partial read is valid ONLY if it captures the complete block/function/table. If a target spans >50 lines, paginate. If ambiguity persists after 3 targeted reads, escalate to `ask_question`.
- **State & MCP Registry**: Maintain agent memory in `.agents/brain/state.json` (schema: `session_id`, `active_plan`, `pending_decisions`, `stack_trace`, `last_action`, `context`). Document available MCP servers in `.agents/brain/mcp-registry.json`. On startup, dynamically discover unknown servers via `list_servers` (or equivalent) and update the registry. Always check the registry before assuming external tool availability.

## 3. Engineering Excellence
- **Holistic Impact**: Evaluate blast radius, future-proofing, scalability, and security before writing code.
- **Framework-Native Tooling**: Always use official CLI generators instead of manual boilerplate. To respect isolation rules, ALWAYS use ephemeral invocations (e.g., `npx`, `pnpm dlx`, `pipx run`) rather than global system installations.
- **UI Frameworks & Dependencies**: Strictly use native UI components if a framework is present. Check dependency files before installing to avoid redundant libraries.
- **Mandatory Testing & Scope**: Measure coverage on changed files only (e.g., using `--changed-files` flag in CI). Maintain 80% coverage for features. *Hotfix Rules*: A `hotfix/` is strictly for urgent production outages/security issues (<2hr SLA), requires `ask_question` approval, and lowers the coverage gate to 60% with mandatory manual QA.
- **Security Baseline**: NEVER hardcode secrets (use env vars; scan via `gitleaks` if possible). Code MUST pass static analysis (SAST like CodeQL) and rigorous linting (`eslint`/`pylint`). These checks are mandatory even for hotfixes. All user inputs must be sanitized using framework-native libraries.
- **Observability Baseline**: Production code MUST include structured JSON logs (INFO for prod, DEBUG for dev) with `trace_id` for correlation. Expose Prometheus metrics (e.g., `/metrics`).
- **Adaptive UI/UX**: Match UI complexity to user intent. For admin panels, prioritize clarity. For consumer views, implement premium aesthetics, micro-interactions, and strict WCAG accessibility (verified via automated tools like `axe-core`).

## 4. Skills & Self-Learning
- **Ecosystem First**: Always check existing `<skills>` and `<mcp_servers>` before writing custom scripts.
- **Controlled Generation**: For recurring tasks, generate a custom skill in `.agents/skills/<name>/`. Extend an existing skill if the core behavior matches ≥80%. Create a new skill if >50% code changes are needed or the domain differs. Deprecated skills must set `deprecated: true` in their frontmatter with a migration path and 30-day grace period.
- **Self-Learning**: Persist newfound solutions via markdown rules in `.agents/brain/rules.md`. When the user invokes the `/learn` slash command, document the new pattern (Problem -> Context -> Solution -> Verification) in rules or generate a new skill.

## 5. Version Control & Collaboration
- **Strict End-to-End Workflow**: Unless the user specifies `!quick` mode, execute sequentially:
  - *(Note: `!quick` mode means skip issue creation, Gitea time tracking, and PR creation. DO NOT skip branching, atomic commits, or merge approval.)*
  1. **Issue Creation**: Create an issue (GitHub/MCP).
  2. **Gitea Time Tracking**: If on Gitea, start the time tracker on the issue.
  3. **Plan**: Create internal `.agents/plans/` checklist.
  4. **Branch**: Create standard prefix branch (`feature/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`, or `quick-` for `!quick` mode).
  5. **Execute & Commit**: Atomic commits with auto-close keywords.
  6. **PR & Cleanup**: Create PR. **Merging to main is a high-stakes action:** you MUST use `ask_question` to get explicit user approval before merging. No override is permitted unless the user explicitly commands "merge without approval". After approval, merge, stop Gitea tracker (if applicable), and delete branch.

## 6. Execution & Safety
- **Skill Sequencing**: The `git-workflow` skill acts as the outer wrapper (Branch → Code → PR). During the *Implementation phase*, execute triggered skills in this order: Architecture Auditor -> Schema Manager -> Implementation -> UI/a11y Reviewer.
- **Error Fallbacks & Retries**: For network/transient errors, retry 3 times with exponential backoff. If it's a permission error, use `ask_permission` first. Otherwise, attempt to use the package manager's native CLI via ephemeral execution (e.g., `npx` or `pnpm dlx`). If that fails, fallback to global invocation only if installed system-wide; otherwise escalate.
- **Artifacts**: Use GitHub-flavored markdown and Mermaid (quote special characters). Use Carousels for sequential step-by-step guides (using the ` ` ` `carousel \n ... <!-- slide --> ... ` ` ` ` format). Use absolute paths starting from the workspace root for links.
- **Isolation & Security Auditing**: Restrict all memory and generated scripts to the local workspace (`.agents/`). No global OS/dependency installations. All external API calls and tool executions MUST be logged to `.agents/brain/audit.jsonl` for security auditing.
