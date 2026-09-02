# Skill Architecture & DRY Rules

This document manages all domain-specific `.agents/skills/<name>/SKILL.md` files.

<DRY_TOKEN_OPTIMIZATION>
- **No Duplication**: If a rule exists in `AGENTS.md` or another `SKILL.md`, DO NOT repeat it here. Use markdown links instead.
- **Telegraphic**: Keep `SKILL.md` files < 50 lines. Remove generic instructions. Focus on precise code checks, API usages, or strict patterns.
- **Modular**: Each skill should focus on ONE explicit domain (e.g., `architecture`, `caveman`, `verification`).
</DRY_TOKEN_OPTIMIZATION>

<TARGET_PROJECT_FOCUS>
- `SKILL.md` files exist to help the agent write better code for the **TARGET PROJECT**, not to over-engineer the agent itself.
- All rules must anchor to tangible target project needs.
</TARGET_PROJECT_FOCUS>

<ANTI_HALLUCINATION>
- `SKILL.md` must enforce `grep_search` and `list_dir` for its specific domain. Example: Before applying a CSS grid, `grep_search` to see if a UI library like Tailwind is already used in the target project.
</ANTI_HALLUCINATION>

## Available Skills
Always consult the specific folder inside `.agents/skills/` for execution details.
- [Caveman Protocol](file://.agents/skills/caveman/SKILL.md) -> Token optimization & exact outputs.
- [Verification](file://.agents/skills/verification/SKILL.md) -> Testing strategies.
- [Architecture](file://.agents/skills/architecture/SKILL.md) -> System design rules.
