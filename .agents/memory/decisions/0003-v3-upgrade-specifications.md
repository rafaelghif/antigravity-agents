# ADR 0003: AAC V3 Aligned Specifications

## Context
During the V3 planning phase, several major upgrades were aligned on to improve verification performance, safety of sandbox executions, cost controls, and agent communication. An interactive interview (via `/grill-me`) was conducted with the user to lock in specifications.

## Decision
We implement the following configuration specifications for AAC V3:

1. **Sandbox Isolation Method:** Lightweight Python virtual environment (`venv`) combined with temporary directories (`tempfile.TemporaryDirectory`). This ensures local verification commands and unit tests run in a clean, throwaway target workspace without needing local Docker daemons.
2. **Swarm Communication Protocol:** Asynchronous, git-tracked JSON message log entries stored under `.agents/messages/`. This mailbox format enables easy debugging, history auditing, and concurrency without active socket servers.
3. **Token budget limits:**
   * Soft limit: 100,000 tokens daily
   * Hard limit: 200,000 tokens daily
4. **Token budget action:** Pause execution dynamically and prompt the developer for confirmation/bypass when the daily token usage exceeds the hard limit.

## Status
Accepted

## Consequences
- Workspace testing will run inside sandboxed venvs to prevent host system filesystem mutations.
- The swarm agent roles will have a stable, file-based exchange channel.
- Large billing runs will be blocked by token budget controls.
