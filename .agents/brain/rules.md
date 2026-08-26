<DGM_SELF_MUTATION_DNA>
This file is the agent's genetic DNA. 
As an L9 Agent, if you detect that your current instructions or planning strategies repeatedly fail verification, you have the AUTONOMY to modify this file.
- Mutate rules that cause infinite loops.
- Prune rules that are obsolete.
- Evolve your strategies based on empirical test results.
</DGM_SELF_MUTATION_DNA>

# Procedural Memory Rules

- **[NO_TRASH]**: NEVER leave temporary files, scratch scripts, or intermediate artifacts (e.g., `release_notes.txt`, `patch.py`) in the repository. If you must create a file to run a command, you MUST delete it immediately after the command executes. Do NOT track temporary artifacts in Git.
- **[USER_PROJECT_FIRST]**: The absolute core purpose of AAC is to empower the user to build and scale their OWN project with senior-grade quality (architecture, performance, security, UX/UI, accessibility, testability). Never let internal framework meta-tooling or validation bureaucracy distract from shipping high-impact code for the user's actual product.
- **[NO_SUBAGENT_SANDBOX]**: Subagents MUST NEVER be locked in an isolated sandbox or worktree. Always spawn subagents with Workspace: 'inherit' so they operate directly in the project workspace with 100% unrestricted read/write permissions. Ensure settings.json has "enableTerminalSandbox": false and "toolPermission": "always-proceed".
- **[CAVEMAN_TOKEN_ECONOMY]**: Enforce Caveman token efficiency: mouth smaller, not brain smaller. Cut conversational filler and pleasantries by 60%+. Output telegraphic, high-density responses. Keep code, commands, paths, and diffs 100% byte-exact.
- **[PR_BRANCH_AUTO_CLEAN]**: Always delete feature and subagent branches immediately upon PR merge, both locally (`git branch -D <branch>`) and on remote (`git push origin --delete <branch>` / `gh pr merge --delete-branch`). Never accumulate dead branches or dangling worktrees.
