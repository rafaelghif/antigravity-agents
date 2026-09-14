# Issue Tracker Configuration

Primary issue tracking configuration for **AAC (Antigravity Agent Core)**.

## Primary Tracker: GitHub

Issues, specifications, and wayfinder maps are tracked on GitHub via `gh` CLI or GitHub MCP tools.

- **Remote**: `origin` -> `https://github.com/rafaelghif/antigravity-agents-core.git`
- **Commands**:
  - Create issue: `gh issue create --title "..." --body "..."`
  - Read issue: `gh issue view <number> --comments`
  - List issues: `gh issue list --state open --json number,title,body,labels,comments`
  - Edit issue / labels: `gh issue edit <number> --add-label "..."`
  - Close issue: `gh issue close <number> --comment "..."`
- **PRs as a request surface**: `no`

## Alternative Tracker: Gitea MCP

When working within local/self-hosted environments, use the Gitea MCP tools configured in `.agents/mcp_config.json` or `.agents/plugins/workspace-integrations/`:
- `call_mcp_tool` with `ServerName: "workspace-integrations_gitea"` (e.g. `issue_read`, `issue_write`, `list_issues`).

## Offline / Local Fallback

For local or solo development without network connectivity:
- Store issue files under `.scratch/tickets/` as markdown files.
