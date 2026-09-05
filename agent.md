# Antigravity Agent Instructions

Read `AGENTS.md` before acting. It is the single source of truth for L9 workflow and conventions.
- **Target**: Ship target project, not agent harness. Existing Project > General Best Practice.
- **Ground**: ALWAYS run `python3 scripts/grounding.py` and inspect files with `view_file` before coding. Never assume stack or APIs.
- **Rules**: Modular rules are located in `.agents/rules/` and skills in `.agents/skills/`.
- **Verify**: Execute tests via `scripts/verify.py --execute --terse`. If unverified, report `NOT VERIFIED`.
