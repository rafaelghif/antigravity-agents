# Typical Workflow for the Agent

This document explains the standard operational sequence that AI software engineering agents (or developers) must follow when implementing features or fixing bugs in this repository.

> [!NOTE]
> **Autonomous Script Execution**: Agents are instructed by the project architectural blueprint ([project_rules.md](file://./../rules/project_rules.md)) to execute these operational commands (locking, validation, API sync, and archiving) automatically without requiring manual user commands.

---

## 1. Typical Step-by-Step Task Execution Loop

When an AI Agent starts working on a task, it must strictly follow these steps to ensure clean history and zero bugs:

1. **Verify State**: Verify that the workspace is on the correct branch and clean.
2. **Lock Module**: Acquire the module lock to prevent conflicts:
   ```bash
   ./.agents/scripts/helper.sh lock <module_name>
   ```
3. **Implement Feature**: Write code & tests under Test-Driven Development (TDD) guidelines.
4. **Staging & Commit**: Stage files and execute the helper commit command:
   ```bash
   ./.agents/scripts/helper.sh commit feat core "add new feature implementation"
   ```
   *(This automatically stages changed files, verifies compliance/tests, rotates Git profile and SSH keys securely, commits, and releases all active locks).*
5. **Handover Relay (Next Turn)**: Before ending a session or switching agent accounts, the agent writes a brief state summary (under 5 lines) in `.agents/memory.md` under `## 3. Relayed Context & Handover Notes` to guide the incoming agent.
6. **Merge Preparation**: Run `./.agents/scripts/helper.sh archive` to compact checklists before merging to `main`/`master`.
