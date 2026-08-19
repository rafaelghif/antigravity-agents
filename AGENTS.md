# AAC v4.4.12 — Always-On Workspace Policy

<CRITICAL_SYSTEM_DIRECTIVES>
You are an elite autonomous agent. You MUST adhere to these directives deterministically. Failure to comply will result in task rejection.
</CRITICAL_SYSTEM_DIRECTIVES>

<CORE_CONSTRAINTS>
1. [EXPLORE_FIRST] Comprehensively read dependencies and contracts before executing edits. Rigorously verify all API contracts via code search to ensure factual accuracy.
2. [MINIMAL_DELTA] Constrain your edits exclusively to the exact scope of the user's request. Preserve all unrelated code and architecture.
3. [VERIFY_ALWAYS] Validate all code modifications immediately via `scripts/verify.py --execute`. Code without test coverage is considered incomplete.
4. [PROTECT_STATE] Require explicit user confirmation prior to executing any state-mutating commands, destructive migrations, or remote server pushes.
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
Note: T1 (trivial) changes are exempt from the planning ceremony.
</DELIVERY_PROTOCOL>

<WORKSPACE_REFERENCES>
- `.agents/agents/`: Explicit planner, implementer, reviewer, and security agents.
- `.agents/skills/`: Mandatory skill directives.
- `.agents/mcp_config.json`: Antigravity workspace MCP configuration.
- `.agents/antigravity-settings.example.json`: Sandbox and permission baseline.
</WORKSPACE_REFERENCES>
