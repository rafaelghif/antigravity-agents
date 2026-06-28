# Pre-Implementation Impact Analysis: Two-Way Offline-to-Online Issue Synchronization

We evaluate two approaches to implement two-way issue synchronization (pushing local issues created offline to GitHub).

## Option A: Direct Inline Integration in `sync_issues`
Incorporate the pushing logic directly inside the existing `sync_issues()` function.
- **Pros**: Single function execution entry point.
- **Cons**: High cognitive complexity. Merging fetch-sync logic with create-push API requests in a single function makes unit testing and error isolation difficult.

## Option B: Modular `push_offline_issues()` helper (Recommended)
Implement a separate function `push_offline_issues()` that audits all local issue files, filters out those lacking a `github_number` or `github_url` frontmatter, uploads them via `git_api.create_github_issue`, and updates their local markdown files with the newly retrieved remote details. We then call this helper in the `sync` action flow in `issue.py`.
- **Pros**: High modularity, separation of concerns, and clean testability. Easy to mock the pushing logic independently of the fetching logic.
- **Cons**: Requires adding a new function to `issue.py`.

### Downstream Impacts
- Modifies `issue.py` to add `push_offline_issues()` and call it in `run(["sync"])`.
- Requires mocking GitHub POST requests in unit tests.

**Decision**: **Option B** is selected.
