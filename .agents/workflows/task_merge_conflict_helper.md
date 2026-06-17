# Task Workflow: Interactive Merge Conflict Resolution Helper

This workflow document acts as the single source of truth for the interactive merge conflict resolution wizard integrated into the `issue merge` process.

---

## 1. Aligned Design Decisions & Execution Plan

### A. Interception & Wizard Triggers
- **Trigger**: When `git merge <branch>` fails during `helper.ps1 issue merge <id>`, catch the error.
- **Conflict Scan**: Identify all conflicted files using `git diff --name-only --diff-filter=U`.
- **Wizard Flow**:
  1. For each conflicted file:
     - Triage structured files (`memory.md` and `CHANGELOG.md`) first.
     - Attempt a Smart Auto-Merge (combining lines, resolving hashes).
     - If smart auto-merge succeeds, mark the file as resolved (`git add <file>`).
     - If it fails, or for code source files, present an interactive menu:
       - `[1]` Use Ours (Feature branch version) -> Run `git checkout --ours <file>` and `git add <file>`.
       - `[2]` Use Theirs (Base branch version) -> Run `git checkout --theirs <file>` and `git add <file>`.
       - `[3]` Open in Default Editor -> Open using Git configured editor (e.g. VS Code, Notepad, nano) and wait for the process to exit, then run `git add <file>`.
  2. Once all files are resolved, complete the merge commit.

### B. Smart Auto-Merge Strategies
- **memory.md**: Parse both versions of the checklist. Union the completed items (`[x]`) and active items (`[/]` or `[ ]`) from both sides, keeping checklist lines deduplicated and sorted.
- **CHANGELOG.md**: Combine version release notes sections under the corresponding version headers, keeping added/changed/fixed lists unified.

---

## 2. Implementation Steps

1. **Modify `cli/commands/issue.py`**:
   - Refactor `merge_issue()` to wrap `subprocess.run(["git", "merge", ...])` in a try-catch or return code check.
   - If return code is non-zero (indicating conflict):
     - Run `get_conflicted_files()`.
     - Implement the interactive conflict resolution wizard.
     - Call `subprocess.run(["git", "commit", "--no-edit"])` or standard commit wrapper to complete the merge.
2. **Add unit tests**:
   - Create tests in `tests/test_issue_command.py` verifying conflict detection, Ours/Theirs choices, and the Smart Auto-Merge logic.
3. **Verify Compliance**:
   - Run the compliance validation suite to verify the changes.
