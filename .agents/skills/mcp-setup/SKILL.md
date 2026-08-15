---
name: mcp-setup
description: Use this skill to initialize the MCP configuration for the workspace. Call this when the user wants to set up external tools or GitHub Copilot integrations.
---

# MCP Setup

1. Check if `.agents/mcp_config.json` already exists.
2. If it does not exist, copy `.agents/mcp_config.json.example` to `.agents/mcp_config.json`.
3. Ask the user for their GitHub Personal Access Token (PAT) or instruct them to define the environment variables required by the config.
4. Provide instructions to the user to reload the agent to apply the MCP servers.
