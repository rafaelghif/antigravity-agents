# AAC v4.4.3 — Always-On Workspace Policy

<CRITICAL_SYSTEM_DIRECTIVES>
You are an elite autonomous agent. You MUST adhere to these directives deterministically. Failure to comply will result in task rejection.
</CRITICAL_SYSTEM_DIRECTIVES>

<CORE_CONSTRAINTS>
1. [EXPLORE_FIRST] Read dependencies and contracts before editing. NEVER hallucinate APIs.
2. [MINIMAL_DELTA] Make the smallest correct change. No unrelated refactors.
3. [VERIFY_ALWAYS] Code without tests or unverified via `verify.py` is considered BROKEN.
4. [PROTECT_STATE] Do not run destructive migrations or remote mutations without explicit user consent.
</CORE_CONSTRAINTS>

<MANDATORY_SKILL_TRIGGERS>
You MUST activate the following skills based on your task. To activate a skill, read its file using the `view_file` tool (e.g., `.agents/skills/architecture/SKILL.md`).
- `architecture`: Trigger for system design, DB schemas, API contracts.
- `code-quality`: Trigger whenever writing or refactoring application code.
- `security`: Trigger for authentication, CI/CD, Docker, or handling user input.
- `verification`: Trigger IMMEDIATELY after editing code to run the self-healing loop.
</MANDATORY_SKILL_TRIGGERS>

<DELIVERY_PROTOCOL>
1. Explore -> 2. Plan -> 3. Execute -> 4. Verify -> 5. Review. 
State your findings concisely. Do not narrate routine reads.
</DELIVERY_PROTOCOL>

## Workspace References
- `.agents/agents/`: Explicit planner, implementer, reviewer, and security agents.
- `.agents/skills/`: Mandatory skill directives.
- `.agents/mcp_config.json`: Antigravity workspace MCP configuration.
- `.agents/antigravity-settings.example.json`: Sandbox and permission baseline.
- `scripts/verify.py`: Stack-aware verification.
