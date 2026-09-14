---
name: handoff
description: >-
  Compacts the current conversation into a handoff document for a subsequent agent session to continue work seamlessly.
  Use when the user asks to create a handoff, prepare context for a new session, or summarize progress for another agent.
---

# Antigravity Session Handoff

Write a handoff document summarizing the current conversation so a fresh agent can continue the work seamlessly. Save it to `.scratch/handoff.md` or the conversation artifact directory.

## Structure & Template

Follow the standardized structure defined in [handoff.template.md](file:///D:/Project/antigravity-agents/docs/templates/handoff.template.md):
1. **Goal**: High-level goal of the session.
2. **Current State**: Active Git branch, commit SHA, and working tree status (`git status`).
3. **Completed Items**: Bulleted list of verified items finished in this session.
4. **Active Decisions & Blockers**: Unresolved architectural choices, domain model shifts, or external blocks.
5. **Immediate Next Action**: Exactly ONE concrete, runnable instruction for the next agent to execute first.
6. **Suggested Skills**: Relevant skills the next agent must inspect via `view_file`.

## Guidelines

- Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by clickable markdown link instead.
- Redact any sensitive information (API keys, tokens, passwords, PATs).
- If the user passed arguments, treat them as a description of what the next session will focus on and tailor the document accordingly.
