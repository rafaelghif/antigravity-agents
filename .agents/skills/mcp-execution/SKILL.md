---
name: "mcp-execution"
description: "Guidelines and strict anti-hallucination protocols for safely executing lazy-loaded MCP tools without guessing JSON schemas."
---

# MCP Execution & Anti-Hallucination Playbook

This playbook outlines the mandatory execution guardrails for AI Agents interacting with external MCP servers (such as GitHub, Gitea, or custom tools).

## 1. The Core Problem: Lazy-Loaded Hallucination
To conserve context tokens, many MCP servers expose tools as **lazy-loaded**. This means the tool names are visible in the context window, but their detailed JSON arguments and usage instructions are **not**. 
When an agent attempts to guess the arguments for a lazy-loaded tool based solely on its name, it frequently hallucinates the JSON payload schema, resulting in an immediate execution failure or syntax error.

## 2. Mandatory Protocol for MCP Tool Execution
Before calling any lazy-loaded MCP tool using `call_mcp_tool`, you MUST execute the following pre-flight steps:

### Step A: Locate the Tool Schema
Identify the target MCP server directory. Tool schemas are stored locally in the agent's MCP cache:
`/home/rafaelghifari/.gemini/antigravity-cli/mcp/<serverName>/<toolName>.json`

### Step B: Read the Schema (No Guessing)
You MUST use the `view_file` (or `read_file`) tool to read the exact `<toolName>.json` schema file.
- **NEVER** skip this step for lazy-loaded tools.
- **NEVER** assume standard API parameter names (e.g., guessing `pull_number` instead of `pullNumber`).

### Step C: Execute with Exact Parity
When crafting your `Arguments` payload for `call_mcp_tool`:
1. Use exact key names as defined in the schema properties.
2. Provide all `required` fields.
3. Validate enum restrictions and data types locally in your thoughts before transmitting the tool call.

## 3. Remote-First Fallbacks
If the MCP server is unreachable, unauthenticated, or fails to execute properly even with correct schemas:
1. Fallback to local offline CLI tools (e.g., `gh pr create` or native Git CLI).
2. If BOTH methods fail, you MUST IMMEDIATELY halt execution and explicitly prompt the Human User with a manual intervention link. DO NOT silently retry endlessly.
