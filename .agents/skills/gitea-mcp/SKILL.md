---
name: gitea-mcp
description: Playbook for configuring and executing Gitea Model Context Protocol (MCP) server commands, supporting repository, branch, release, tag, issue, and wiki management.
---

# Gitea MCP Skill Playbook

This playbook provides standard setup instructions, configuration references, and operational commands for Gitea MCP Server integrations.

## 1. Core Principles
* **Parameter priority**: Personal access tokens and host configuration can be provided via environment variables or command-line args. Arguments take precedence.
* **Server limitations**: Page counts and maximum response sizes for listing commits, branches, or issues are silently capped by the Gitea server's `[api].MAX_RESPONSE_ITEMS` setting (default: 50).

## 2. Configuration & Commands Reference

### Option A: Local Containerized Server (Docker-based)
Run the Gitea MCP server container locally:
```bash
docker run -i --rm -e GITEA_ACCESS_TOKEN=<YOUR_TOKEN> -e GITEA_HOST=<GITEA_HOST_URL> docker.gitea.com/gitea-mcp-server
```

IDE configuration for local container:
```json
{
  "gitea": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e",
      "GITEA_ACCESS_TOKEN",
      "-e",
      "GITEA_HOST",
      "docker.gitea.com/gitea-mcp-server"
    ],
    "env": {
      "GITEA_ACCESS_TOKEN": "<YOUR_TOKEN>",
      "GITEA_HOST": "<GITEA_HOST_URL>"
    }
  }
}
```

### Option B: Local Native CLI Binary (Golang-built)
If running Gitea MCP natively:
```json
{
  "gitea": {
    "command": "gitea-mcp",
    "args": [
      "-t",
      "stdio",
      "--host",
      "https://gitea.com"
    ],
    "env": {
      "GITEA_ACCESS_TOKEN": "<YOUR_TOKEN>"
    }
  }
}
```

## 3. Implementation Checklist & Verification
* [ ] Confirm that Gitea host URL (`GITEA_HOST`) is fully accessible and includes correct schema (`https://`).
* [ ] Verify that `GITEA_ACCESS_TOKEN` is generated with appropriate permissions.
* [ ] Test query in chat: `list all my repositories` or `list repository commits` to verify integration.

## 4. References & Documentation
* [Google Antigravity MCP Guide](https://antigravity.google/docs/mcp)
* [Gitea MCP Server Repository](https://gitea.com/gitea/gitea-mcp)
