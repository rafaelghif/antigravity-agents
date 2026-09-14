---
name: subagent-handoff
description: >-
  Hands off the current conversation to an autonomous background subagent via invoke_subagent.
  Use when the user asks to spin off a background agent, delegate the session, or continue work asynchronously.
---

# Antigravity Subagent Handoff

Compacts the current conversation state into a structured handoff prompt and spawns an autonomous subagent via `invoke_subagent` to continue work in the background.

## Process

1. **Synthesize Handoff Prompt**:
   - Objective & current goal.
   - What has been done (completed files, tests run, decisions made).
   - What remains to be done (concrete next steps).
   - Context pointers: point directly to repository files using `file:///` markdown links (e.g. `[AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md)`).
   - Suggested skills for the subagent to inspect via `view_file`.

2. **Spawn Autonomous Subagent**:
   Call `invoke_subagent` with the synthesized prompt:

   ```json
   {
     "Subagents": [
       {
         "Role": "Handoff Worker: <descriptive name>",
         "TypeName": "self",
         "Model": "flash",
         "Workspace": "inherit",
         "Prompt": "<synthesized handoff prompt>"
       }
     ]
   }
   ```

3. **Confirm Launch**:
   - Inform the user that the background subagent has been dispatched with its returned `conversationId`.
   - Remind the user that progress can be monitored via `manage_subagents` (`Action: "list"`).
