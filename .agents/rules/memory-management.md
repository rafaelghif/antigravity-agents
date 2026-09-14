---
trigger: always_on
---

# Antigravity Memory Management & Cross-Session Protocol

Operational guidelines for managing working memory within a session and bridging context across different sessions.

---

## 1. Five-Tier Memory Hierarchy

Antigravity enforces strict context isolation across sessions. Context is partitioned into five distinct tiers:

1. **Tier 1: Ephemeral Working Context (Intra-Session)**
   - Lives only within the active session context window and transcript log (`transcript.jsonl`).
   - Reset upon starting a new session. Controlled via Progressive Disclosure (read skills via `view_file` only on-demand).
2. **Tier 2: Unconditional Workspace Directives (Cross-Session Deterministic)**
   - [AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md) and [.agents/rules/](file:///D:/Project/antigravity-agents/.agents/rules) (`trigger: always_on`).
   - Injected unconditionally every turn. Keep concise (<12,000 chars in `AGENTS.md`). Never store ephemeral task logs here.
3. **Tier 3: Domain & Architectural Knowledge (Living Docs)**
   - [CONTEXT.md](file:///D:/Project/antigravity-agents/CONTEXT.md): Living domain models, bounded contexts, and glossary.
   - [docs/adr/](file:///D:/Project/antigravity-agents/docs/adr): Immutable Architectural Decision Records. Read on-demand when touching domain boundaries.
4. **Tier 4: Session Bridge Handoff (Inter-Session State)**
   - Bridge artifact: `.scratch/handoff.md` (generated via [handoff](file:///D:/Project/antigravity-agents/.agents/skills/handoff/SKILL.md)).
   - Checkpoint state before exiting or switching tasks. Rehydrate in new sessions via `@handoff.md` or `conversation://<id>`.
5. **Tier 5: External Task Graph (Durable Frontier)**
   - Issue Tracker (Gitea / GitHub issues via MCP tools).
   - External source of truth for work items (`to-tickets`, `wayfinder`, `triage`).

---

## 2. Cross-Session Execution Protocol

### Closing a Session (Checkpointed Exit)
Before ending a long session or handing off:
1. Verify working tree is committed with conventional commits (`git status ; git commit`).
2. Run [handoff](file:///D:/Project/antigravity-agents/.agents/skills/handoff/SKILL.md) to generate `.scratch/handoff.md` containing:
   - **Goal**: One-sentence purpose of the session.
   - **Current State**: Active Git branch, latest commit SHA, modified files.
   - **Completed Items**: Verified functional increments.
   - **Blockers / Decisions**: Pending architectural choices or external dependencies.
   - **Immediate Next Action**: Exactly one concrete, runnable instruction for the next agent.
   - **Suggested Skills**: Skills the next agent must load via `view_file`.
3. Update issue status on Gitea/GitHub if applicable.

### Starting a New Session (Cold-Start Rehydration)
When starting in a fresh session:
1. Workspace rules and [AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md) load automatically.
2. If `.scratch/handoff.md` exists or the user mentions `@handoff.md`, inspect it first via `view_file`.
3. Read [CONTEXT.md](file:///D:/Project/antigravity-agents/CONTEXT.md) only if the task touches domain modeling or architecture.
4. Execute the **Immediate Next Action** stated in the handoff document immediately.

---

## 3. Persistent Learning (`/learn`)

When user provides workflow corrections or project-specific operational adjustments:
- Persist the rule into `.agents/rules/` or [AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md) so future sessions retain the behavior.
