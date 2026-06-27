# Pre-Implementation Impact Analysis

## Issue ID: issue-029
## Title: Implement automated branch merge and board transition in issue close command

This analysis compares Option A and Option B for automating the transition and merging of task/issue branches.

---

### Option A: Integrated Atomic "Close and Merge" Flow (Recommended)
In this option, the `./helper.sh issue close <id>` command is extended to handle the entire closure lifecycle.

#### Action Sequence:
1. Run local validation checks (`validate.py`). If they fail, abort.
2. Update the issue markdown file to `status: closed`.
3. Update the task board `.agents/tasks/board.md` to move the task from `Todo`/`Doing` to `Done` and check it.
4. Run the SemVer changelog generator (`changelog.py`) to bump the version and update CHANGELOG.md.
5. Automatically stage and commit all files modified by the task (including `board.md`, the issue file, and changelog changes) on the feature branch.
6. Switch to the base branch (`main` or `master`).
7. Merge the feature branch into the base branch cleanly.
8. Delete the local feature branch.
9. Release active locks associated with the branch.

#### Pros:
- Single command to complete a task. Zero chance of a developer/agent closing an issue but forgetting to merge it.
- Prevents dirty base branch modifications because everything is committed on the feature branch before merge.
- Natively compliant with all strict rules.

#### Cons:
- Slightly longer execution time for the `close` command due to validation, but it guarantees correctness.

---

### Option B: Separate "merge" Subcommand
In this option, we introduce a new command `./helper.sh issue merge <id>`, keeping `./helper.sh issue close <id>` strictly for updating the issue status.

#### Pros:
- Separate concerns.

#### Cons:
- Double the steps. Agents or other developers might run `close` but forget to run `merge`, leaving branches dangling.

---

### Recommendation
**Option A** is the recommended approach. By automating the entire lifecycle inside `issue close <id>`, we ensure that no task is ever marked finished without its corresponding git branch being merged back to `main`/`master` and cleaned up.
