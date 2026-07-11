# ADR 0004: Relocate soul.md to .agents Root

## Context
The agent's "soul" profile (soul.md) defines the AI core's persona, guidelines, mission, and communication tone. It is a static, systemic property of the agent framework. Previously, it was stored under `.agents/memory/soul.md`. However, because `.agents/memory/*` is globally excluded during framework installation and bootstrapping to prevent overwriting project-specific mutable memory, `soul.md` was missed during clean installations, causing diagnostic heartbeat warnings.

Additionally, semantically, the agent's identity (soul) is a system configuration file that should update with framework upgrades, rather than mutable workspace memory.

## Decision
We decided to relocate `soul.md` from `.agents/memory/soul.md` to `.agents/soul.md` (the root of the `.agents/` directory). This separates the agent's core identity from the project's mutable memory state. 

We will update the following components:
1. `heartbeat.py` to point to `.agents/soul.md`.
2. `bootstrap.py` to include `.agents/soul.md` in the core files helper copy list.
3. `context_map.md` to reference `.agents/soul.md`.
4. The installers do not exclude files in the root of `.agents/` unless explicitly ignored, so `soul.md` will be copied by default.

## Status
Accepted

## Consequences
- Clean installations will automatically copy the agent's soul profile to the target workspace.
- The heartbeat check will pass cleanly out-of-the-box.
- Segmenting identity from project memory simplifies the template/memory model.
