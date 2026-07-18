---
name: swarm-orchestration
description: Playbook for delegating tasks to subagents, utilizing isolated branch workspaces to prevent code conflicts, and aggregating pull requests.
---

# Swarm Orchestration Playbook

This playbook defines the strict protocol for the Parent Agent to decompose large epics and orchestrate multiple autonomous subagents concurrently without code conflicts.

## Phase 1: Task Decomposition & Issue Generation
Before spawning any subagents, the Parent Agent must prepare the specifications:
1. **Breakdown**: Divide the main Epic into strictly independent, non-overlapping subtasks.
2. **Generate Specs**: For each subtask, create a formal local issue spec using `./helper.sh issue create <subtask-id> "<title>"`.
3. **Detailed Criteria**: Edit the newly created `.agents/issues/<subtask-id>.md` file to include explicit Acceptance Criteria and constraints. A subagent will only know what is written in this file.

## Phase 2: Spawning Subagents (Isolation Protocol)
To prevent Git conflicts and filesystem race conditions, subagents MUST NOT share the same active working tree.
1. Use the `invoke_subagent` native tool to spawn the workers.
2. **CRITICAL ARGUMENT**: You MUST set the `Workspace` argument to `branch`. This creates an isolated feature branch for the subagent, ensuring they can work in parallel safely.
3. Instruct the subagent to read their specific `.agents/issues/<subtask-id>.md` file and execute the task.

## Phase 3: Subagent Execution (Directives for the Subagent)
If you are a subagent reading this playbook, you must adhere to the following workflow:
1. Initialize by reading your assigned `.agents/issues/` specification file.
2. Write code and execute local validation (`./helper.sh validate`).
3. Commit your changes locally to your isolated branch.
4. Push your branch to the remote repository.
5. Create a Pull Request (PR) against the Parent Agent's branch using the Git MCP tools (or `gh` CLI fallback). Do NOT merge directly!

## Phase 4: Aggregation and Conflict Resolution
1. The Parent Agent waits for subagents to complete their PRs.
2. Review the Pull Requests submitted by the subagents.
3. Handle any minor merge conflicts locally if necessary.
4. Merge the PRs into the main Epic branch, close the local `.agents/issues/` subtasks, and finalize the Epic.
