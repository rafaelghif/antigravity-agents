# ADR 0001: Initialization of V2 Layout

## Context
As the codebase grows, V1 guidelines and layout structure accumulated redundant documentation files and a monolithic script setup. To enhance prompt caching efficiency, minimize token waste, and clarify developer conventions, we need a lighter, more structured directory blueprint (V2).

## Decision
We initialize Antigravity Agent Core V2 (AAC V2) with a flat, modular directory design matching the new `AGENTS.md` context map. 

The structure comprises:
1. `AGENTS.md` in root acting as the master rules file (under 150 lines).
2. `.agents/tasks/board.md` for task state.
3. `.agents/memory/` containing architecture summaries, glossary, tech-debt logs, and ADRs under `.agents/memory/decisions/`.
4. `.agents/skills/` containing localized skill playbooks (`SKILL.md`).
5. `.agents/workflows/` containing slash-command macros.

## Status
Accepted

## Consequences
- Prompt caching hits will be optimized because unchanged documentation and schemas are cached, while only transient task logs change.
- Strict isolation of files prevents cross-domain pollution.
- Development of CLI tools will follow modular command layouts under Python.
