# ADR-004: Clean Project Isolation for Injected Agent Setup

## Status
Accepted

## Context
When the Antigravity Agent framework is injected into an existing codebase (host project), it must not conflict with or disrupt the host project's configuration, documentation, environment, or secret files.
Specifically:
- Root-level markdown files (e.g., `README.md`, `CHANGELOG.md`, `MIGRATION.md`) are standard for any repository. If the agent framework places its own guides in the root, it will overwrite the host project's documentation.
- Editing the `.gitignore` file programmatically during migration or validation could mess up the host project's existing ignore rules if done blindly.
- Overwriting or editing the host project's `.env` or other configuration files to manage agent API keys could lead to credential leaks or application startup failures.

## Decision
We will enforce the following isolation patterns across the workspace:

1. **Encapsulated Documentation:**
   - Move all agent-specific documents (`MIGRATION.md`, `CHANGELOG.md`, and the agent framework `README.md`) inside the `.agents/` directory (e.g., `.agents/docs/README_AGENT.md`, `.agents/docs/MIGRATION.md`, `.agents/docs/CHANGELOG.md`).
   - Keep only `AGENTS.md` at the project root, as it serves as the universal entry point / boot protocol for incoming agents.

2. **Scoped `.gitignore` Blocks:**
   - Modify the automated `.gitignore` updater in the helper script (`helper.sh`) to insert and update agent-specific rules inside clearly defined block comments:
     ```gitignore
     # <<< ANTIGRAVITY AGENT START >>>
     # Ignore agent transient locks
     .agents/locks/
     # Ignore local agent API key configuration and active state files
     .agents/api_keys
     .agents/active_api_keys
     .agents/active_api_keys.ps1
     .agents/active_api_profile_name
     # <<< ANTIGRAVITY AGENT END >>>
     ```
   - The script will search for these guards and only modify the content within them, preserving the rest of the host project's `.gitignore` completely.

3. **Ephemeral Environment Subshells:**
   - The key rotation wrapper (`api-rotate-wrapper.sh` / `api-rotate-wrapper.ps1`) will load API keys transiently using subshell sourcing (`source` or call operator) when executing wrapped commands.
   - The host project's `.env` or other configurations will never be read, modified, or appended by the agent framework, ensuring total separation of concerns.

## Consequences
- **Pros:**
  - Zero conflict with the host project's documentation.
  - The project root remains clean and standard.
  - Safe, repeatable, and clean Gitignore configuration updates.
  - Total isolation of runtime API keys and secrets.
- **Cons:**
  - Developers need to look inside `.agents/docs/` to read the agent wrapper documentation.
