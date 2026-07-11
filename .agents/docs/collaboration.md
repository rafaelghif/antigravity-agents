# 🤝 AGENT-HUMAN COLLABORATION PROTOCOL
### *Guidelines for Pair Programming and Task Collaboration in AAC V3*

## 1. Requesting Reviews & Verification
* **Commit Verification**: All code changes proposed or written by the agent MUST pass local validation. If working alongside a human developer, the human may request a manual validation run using `./helper.sh validate` or review changes on a designated feature branch.
* **Code Reviews**: For architecturally significant changes, the agent must not self-merge. The agent should submit a Pull Request or issue a review request to a human contributor or invoke the `code-review` skill.

## 2. Module Locking & Ownership Guidelines
To prevent parallel modifications and merge conflicts:
* **Acquisition**: Both agents and humans should lock modules before editing. Run `./helper.sh lock <module-path>` to register lock ownership.
* **Release**: Once changes are committed and verified, run `./helper.sh lock release <module-path>`.
* **Override Policy**: Humans have ultimate authority. If a lock is held by an idle agent or a stale branch, a human may override it by running the lock CLI command with `--force` (or manually cleaning `.agents/state/locks.json`). Agents must **NEVER** bypass or force-override a lock held by a human developer or another active branch.

## 3. Task Delegation & Specification Checklists
* **Task Board (`board.md`)**: The single source of truth for work items. Task states (Todo, Doing, Done) are updated automatically during issue checkout and closure.
* **Issue Specifications (`.agents/issues/issue_[id].md`)**: Before start of code writing, the agent splits the task into atomic subtasks. Humans may edit this checklist to guide the agent's implementation path.

## 4. Conflict Resolution Protocol
* **Merge Conflicts**: If a merge conflict occurs, the agent will halt and report the conflicting lines. The developer should resolve the conflict using git, or instruct the agent on the resolution strategy.
* **Workspace Desynchronization**: If the active context or task board gets out of sync, run `./helper.sh context optimize` or `./helper.sh sync` to repair.
