# AGENTS.md — Antigravity Agent Core (AAC) V4

**Core Version**: 4.1.0

This core directive governs all agents in this workspace. Reference `.agents/config.json` for all numeric constants and `.agents/common/utils.md` for shared utilities.

## 1. Core Principles & Autonomy
- **Proactive Execution**: Operate autonomously. Use `ask_question` for critical decisions (schema changes, modifying `.agents/`). If a timeout occurs (see `.agents/config.json`), trigger the **Safe Abort Protocol** (stop trackers, close handles, `git stash push -u -m "agent-abort-backup-<timestamp>"` if in progress, log to `.agents/incidents/abort-<timestamp>.json`, and print a direct message to the user). Use `ask_permission` *strictly* for OS-level permission errors.
- **Tenacity vs. Escalation (Rollback Protocol)**: Track attempted approaches with SHA of approach definition. Increment counter only when approach differs by >30%. If distinct approaches fail (limit in `.agents/config.json`): (1) Revert to the branch-start commit if isolated, or `git revert <bad-commit>` if shared, (2) Document in `.agents/incidents/`, (3) Escalate via `ask_question` with a summary of failures.
- **Rule Precedence**: `AGENTS.md` ALWAYS overrides any `.agents/skills/*.md`.

## 2. Anti-Hallucination & State Management
- **Zero-Assumption**: Verify via tools; never guess file contents or API props.
- **Directory Manifest**: 
  - `.agents/scratch/`: Ephemeral notes, context compaction.
  - `.agents/brain/`: `schema.md`, `state.json`, `mcp-registry.json`, architectural records.
  - `.agents/incidents/`: Failed task reports.
  - `.agents/plans/`: Task checklists.
  - `.agents/skills/`: Operational skills.
- **State Management Protocol**: Maintain memory in `.agents/brain/state.json`. Use atomic writes (write to `.agents/brain/state.json.tmp` and `mv` to `.agents/brain/state.json`) to prevent locks. Schema-validate on read. State includes `current_branch`. Delete `.agents/scratch/*` on successful task completion; preserve on failure. Update `.agents/brain/mcp-registry.json` at task start.
- **Error Taxonomy**: 
  - Transient Network (ECONNRESET, ETIMEDOUT): Retry with backoff (see `.agents/config.json`).
  - Permission (EACCES, EPERM): `ask_permission`.
  - Validation (Schema mismatch): Rollback + incident.
  - Logic (Null pointer): Halt + escalate.
  - Dependency (Missing package): Execution Manager.

## 3. Version Control & Collaboration
- **Strict Workflow**: Unless `!quick` mode is specified, execute sequentially: Issue -> Gitea Tracker -> Plan -> Context Compaction -> Branch -> Code -> PR.
- **Branching**: Use standard prefixes (`feature/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`). In `!quick` mode, use format `<prefix>/quick-<slug>` (e.g., `feature/quick-<slug>`).
- **Merge Gate**: Merging to `main` REQUIRES explicit confirmation: user must type `/merge-confirm` with the ticket ID. No substring matching allowed.

## 4. Execution & Safety
- **Skill Execution**: Load `.agents/skills/<name>/SKILL.md` dynamically only when triggered. Ensure skill frontmatter requires compatible core version (`requires_core: ">=4.0.0"`). Verify dynamic skill SHA-256 hashes on execution against expected signatures rather than relying on a single start-of-task `manifest.json`. If mismatch during execution, `ask_question` to update manifest or abort.
- **Orchestration Sequence**:
  1. `architecture-auditor` (if change > 10 lines)
  2. `schema-manager` (if DB changes) -> `architecture-auditor` (max 1 re-audit cycle; escalate via ask_question if loop persists)
  3. `execution-manager` (if dependencies needed)
  4. Implementation
  5. `ui-a11y-reviewer` and `performance-profiler` (can run concurrently)
  6. `security-observability-auditor` (always, halt if fails)
  7. `git-workflow` (PR and merge)
- **Ephemeral Tooling**: ALWAYS use ephemeral invocations (e.g., `npx`, `pnpm dlx`). No global installations.
- **Error Fallbacks**: For network errors, retry (see `.agents/config.json`) with backoff. If permanently unreachable, halt execution and escalate immediately.
- **Logging Infrastructure**: All external API calls and tool executions MUST be logged to `.agents/brain/audit.jsonl` (Rotate daily or limit size to 10MB). Implement automatic redaction of known secrets in audit logs before writing using regex filters (see `.agents/common/utils.md`). No secrets in `.agents/`.
