---
name: github-mcp
description: Playbook for setting up and managing the GitHub Model Context Protocol (MCP) server, supporting both local containerized transport and remote Copilot endpoint configurations.
---

# GitHub MCP Skill Playbook

This playbook provides standard guidelines, configuration references, and operational commands for integrating the official GitHub MCP Server within client environments.

## 1. Core Principles
* **Authentication priority**: Environment variables (such as GITHUB_PERSONAL_ACCESS_TOKEN) take precedence over dynamic OAuth browser sessions.
* **OAuth callbacks**: When using local Docker OAuth flow, port `8085` must be published (`-p 127.0.0.1:8085:8085`) to loopback so the login callback is reachable.
* **Scopes / Permissions**: Keep tokens scoped strictly to what is required (`repo`, `read:org`, `read:packages`).

## 2. Configuration & Commands Reference

### Option A: Local Containerized Server (Docker-based) [Default & Recommended]
Connects directly to the GitHub platform API (`api.github.com`) to manage repositories, issues, pull requests, and projects.
Run the local MCP server inside a Docker container:
```bash
docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN=<YOUR_GITHUB_TOKEN> ghcr.io/github/github-mcp-server
```

IDE configuration for the local container:
```json
{
  "github": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e",
      "GITHUB_PERSONAL_ACCESS_TOKEN",
      "ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_GITHUB_TOKEN>"
    }
  }
}
```

### Option B: Remote GitHub Copilot Endpoint (Disabled by default)
Connects to the remote Copilot HTTP backend:
```json
{
  "github-copilot": {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
      "Authorization": "Bearer <YOUR_GITHUB_TOKEN>"
    }
  }
}
```

## 3. Implementation Checklist & Verification
* [ ] Verify that GITHUB_PERSONAL_ACCESS_TOKEN or `github_mcp_pat` has valid API permissions.
* [ ] Confirm that CLI tool searches (`tool-search`) run successfully from the container.
* [ ] Test query in chat: `list issues in this repository` to verify connectivity.

## 4. References & Documentation
* [Google Antigravity MCP Guide](https://antigravity.google/docs/mcp)
* [GitHub MCP Server Repository](https://github.com/github/github-mcp-server)
