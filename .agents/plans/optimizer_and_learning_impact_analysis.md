# Pre-Implementation Impact Analysis: Context Optimizer & Self-Learning Memory

## 1. Context Optimizer (`context.py`)

We evaluate two approaches to optimize the prompt context for the developer agent without compromising compliance with strict workspace rules.

### Option A: Dynamic `AGENTS.md` Stripping
Directly modify and strip unused skills and guidelines from `AGENTS.md` depending on the active issue.
- **Pros**: Direct reduction of the primary prompt context.
- **Cons**: High risk of accidentally removing non-negotiable rules or core guidelines, violating Git tracking consistency, and breaking skill loading registers.

### Option B: Focused Workspace Task Manifest (`active_context.md`)
Create a dedicated `.agents/active_context.md` that outlines the precise file scope, active subtasks, locked modules, and issue requirements.
- **Pros**: Safely isolates the task context, guarantees 100% of the core rules in `AGENTS.md` remain intact and active, and is cleanly tracked in Git.
- **Cons**: Requires a minor pointer in the prompt to read the active context.

**Decision**: **Option B** is selected to preserve absolute rule strictness.

---

## 2. Memory Synthesizer (`sync_memory.py`)

We evaluate two options for converting unstructured lessons from `lessons-learned.md` into active agent rules in `.agents/rules.md`.

### Option A: Complete Regeneration of `rules.md`
Overwrite `.agents/rules.md` entirely using a static base template and appending lessons.
- **Pros**: Easy to implement.
- **Cons**: Wipes out custom, manually-defined project rules written by the developer in `.agents/rules.md`.

### Option B: Block-Targeted Rule Appending
Maintain a dedicated `# Synthesized Rules` section at the bottom of `.agents/rules.md` and dynamically update only that section.
- **Pros**: Safely preserves user-defined custom rules while keeping the self-learning rules updated.
- **Cons**: Requires more structured string parsing.

**Decision**: **Option B** is selected for safety and flexibility.
