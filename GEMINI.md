# Workspace Bootstrap

Read `AGENTS.md` before acting. It is single source of truth for L9 workflow.
- **Target**: Ship target project, not agent harness. Existing Project > General Best Practice.
- **Ground**: ALWAYS run `python3 scripts/grounding.py` and inspect files with `view_file` before coding. Never assume stack or APIs.
- **Verify**: Execute tests via `scripts/verify.py --execute --terse`. If unverified, report `NOT VERIFIED`. Never hallucinate results.

