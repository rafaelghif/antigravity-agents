# Pre-Implementation Impact Analysis: Fix CLI Sync command to compile lessons to rules

We evaluate two options to fix the CLI sync command to ensure lessons learned compile into rules.md.

## Option A: Add `sync_lessons_to_rules` call to CLI sync command (Recommended)
Modify `.agents/scripts/cli/commands/sync.py` to dynamically call `sync_module.sync_lessons_to_rules()` alongside `sync_skills_to_agents_md()` and `sync_adrs_to_architecture_md()`.
- **Pros**: Matches the existing dynamic import pattern, preserves DRY, and has a minimal footprint.
- **Cons**: None.

## Option B: Inline Compilation Logic in CLI Sync command
Inline or re-write the compilation code inside `.agents/scripts/cli/commands/sync.py`.
- **Pros**: None.
- **Cons**: Duplicates code from `.agents/scripts/sync.py` and violates DRY principles.

### Downstream Impacts
- Fixes the gap where rules.md was not being updated with self-learning lessons.
- Enhances agent rule adherence by bringing lessons learned back into the context rules.

**Decision**: **Option A** is selected.
