# Pre-Implementation Impact Analysis

## Issue ID: issue-039
## Title: Automatically publish GitHub Release Draft during release bump

This analysis compares the chosen design options for this task.

---

### Option A: Direct JSON Payload Release API (Recommended)
We implement `create_github_release(tag_name, name, body, draft)` in `git_api.py` and hook it into `changelog.py` after the changelog is successfully written.

The release description is constructed directly from the same conventional commit categorizations added to `CHANGELOG.md`.

#### Pros:
- 100% automated draft release preparation.
- Uses parsed Markdown notes instead of requiring a separate shell call.
- Completely skipped if token is missing.

#### Cons:
- None.

---

### Option B: Post-Release GitHub Actions Workflow Trigger
Instead of publishing from the CLI directly, let a separate GitHub Action trigger on tag push and publish the release.

#### Pros:
- Fully runs on GitHub side.

#### Cons:
- Doesn't allow developers to publish draft notes directly from the issue-close command when they work locally with remote tracking.

---

### Recommendation
**Option A** is the recommended choice because it integrates with local-remote sync workflow immediately upon closing an issue or running changelog.
