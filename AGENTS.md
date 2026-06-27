# AGENTS.md — Antigravity Agent Core (AAC) V2

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand — see the context map below.

## 1. What this project is
- **Product:** Antigravity Agent Core (AAC) V2 — a highly optimized, project-agnostic operational workspace layout and developer protocol designed specifically for agentic coding, prompt caching, and context insulation.
- **Stack:** Python 3
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
*(Listed first and emphasized — the model weights early, ALWAYS/NEVER-style rules more reliably than buried prose.)*

- **NEVER** commit secrets, `.env*` files, or credentials. Use the secrets approach documented in `.agents/memory/architecture.md`.
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work, and update it when status changes.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first — supersede an old one, don't duplicate it.
- **ALWAYS** use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`) with the task ID in the body.
- **NEVER** run or write raw CLI scripts directly in the workspace root; keep them organized in target directories.
- **ALWAYS** register any new custom skills in their respective subdirectory with a `SKILL.md`.
- **ALWAYS** acquire locks on modules before beginning edits to avoid conflicting parallel modifications.
- **ALWAYS** run `.agents/scripts/validate.py` locally and verify it passes before proposing commits or pull requests.
- **ALWAYS** align your git branch name with an active issue ID and verify a matching issue file exists under `.agents/issues/` (e.g. branch `feat/issue-12` aligns with `.agents/issues/issue_12.md`).
- **ALWAYS** strictly conform to the schemas defined in `.agents/schema.md` when modifying database models or API contracts.
- **NEVER** write to or rely on global configurations outside the project directory (e.g., in user home directory). Everything must be stored strictly within the workspace level under `.agents/` and tracked in git to ensure multi-developer environment consistency.

## 3. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, non-negotiables, map | Always — every prompt |
| `.agents/skills/adr-writer/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/debugging/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/security-audit/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/tasking/SKILL.md` | Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/world-class-programmer/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand, referenced from architecture.md and the `adr-writer` skill — never auto-loaded |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.md` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |

If you're about to paste a paragraph of explanation into this file, it almost certainly belongs in a skill or memory file instead, pulled in with `@path` only when needed. That's what keeps the per-prompt token cost flat as the project grows.

## 4. Working protocol
1. **Before coding:** read `.agents/tasks/board.md`, claim the task, move it to `Doing`.
2. **Pre-Implementation:** Perform a Pre-Implementation Impact Analysis comparing at least two options (following the `world-class-programmer` playbook) to evaluate long-term maintenance and UI/UX simplicity.
3. **Before any architecture-affecting change:** pull `@.agents/memory/architecture.md` and check `.agents/memory/decisions/` for a relevant ADR.
4. **While working:** prefer invoking an existing skill over re-deriving a workflow from scratch.
5. **Before marking a task `Completed`:** tests pass, board updated with implementation notes, and — if the change was architecturally significant — a new or superseding ADR exists (`adr-writer` skill).
6. **End of session:** run `/sync-memory` to fold session learnings into memory and prune anything stale (see `.agents/workflows/sync-memory.md`).

## 5. Git & review
- Branches: `feat/<task-id>-slug`, `fix/<task-id>-slug`.
- One task = one PR where practical; link the task ID in the PR description.
- No self-merging architecturally significant PRs — a second reviewer (human or the `code-review` skill) signs off first.

## 6. Tool permissions
Default to `request-review` in `agy config` for this repo (pauses before destructive/file-write actions). Reserve `proceed-in-sandbox` for disposable environments only. Never set `always-proceed` on a repo with reachable production credentials.

## 7. Maintaining this file
Reviewed like code. Budget: stay under ~150 lines. If it grows past that, move the newest, least-universal addition into a skill or memory file and leave a one-line pointer here instead.
