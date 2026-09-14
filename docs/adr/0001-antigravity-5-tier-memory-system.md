# 1. Antigravity 5-Tier Memory Management System

Date: 2026-09-14
Status: Accepted

## Context

Google Antigravity enforces strict context isolation per session. Relying on raw conversation history across sessions causes rapid token consumption, context pollution, and attention degradation for Gemini 3.8 Flash. We need a standardized, deterministic memory system that guarantees continuity across sessions while preserving minimal context usage.

## Decision

We adopt a **5-Tier Memory Architecture** within the repository:

1. **Tier 1 (Ephemeral Working Context)**: Managed via Antigravity's progressive disclosure. Only skill names/descriptions load initially; detailed procedures load on-demand via `view_file`.
2. **Tier 2 (Unconditional Directives)**: [AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md) (<12k chars) and [.agents/rules/](file:///D:/Project/antigravity-agents/.agents/rules) with `trigger: always_on`.
3. **Tier 3 (Domain & Architectural Knowledge)**: Living [CONTEXT.md](file:///D:/Project/antigravity-agents/CONTEXT.md) and immutable ADRs under `docs/adr/`.
4. **Tier 4 (Session Bridge Handoff)**: Compact `.scratch/handoff.md` written by the exiting agent via [handoff](file:///D:/Project/antigravity-agents/.agents/skills/handoff/SKILL.md) and rehydrated via `@handoff.md` or `conversation://<id>`.
5. **Tier 5 (External Task Graph)**: Issue trackers (Gitea / GitHub) via MCP as the durable source of truth.

## Consequences

- **Positive**: Eliminates cross-session context bloat; enables immediate cold-start onboarding for fresh agent sessions; persists domain decisions cleanly.
- **Trade-off**: Requires discipline to generate a handoff document (`/handoff`) prior to ending long sessions or switching tasks.
