---
title: Git & GitHub CLI Operational Guidelines
version: 1.0.0
last_updated: 2026-06-17
owner: Antigravity Agent Maintainers
applies_to: All AI agents and developers operating in this workspace
status: Draft for review
related_docs:
  - AGENTS.md (Global Agent Protocol)
  - .agents/rules/project_rules.md (Project Architecture Blueprint)
  - .agents/skills/git-ops/SKILL.md (git-ops skill — git-only workflow)
  - .agents/scripts/helper.sh (Antigravity helper CLI)
  - .agents/hooks/pre-commit (commit gate)
---

# Git & GitHub CLI Operational Guidelines

> **Scope.** This document defines the safe, auditable, and reversible patterns for using `git` and `gh` (the GitHub CLI) in this workspace. It supplements — and where it conflicts with — `AGENTS.md`, `project_rules.md`, and the `git-ops` skill. When this document and `AGENTS.md` disagree, **the stricter rule wins**.
>
> **Audience.** Any agent or developer that mutates the repository, opens / reviews / merges PRs, or interacts with GitHub programmatically.

## Contents

1. [Core Principles](#core-principles)
2. [Git](#git)
   - 2.1 [Protected branches](#21-protected-branches)
   - 2.2 [Default-branch detection](#22-default-branch-detection)
   - 2.3 [Staging discipline](#23-staging-discipline)
   - 2.4 [Destructive operations](#24-destructive-operations)
   - 2.5 [Commits & history rewriting](#25-commits--history-rewriting)
   - 2.6 [Editor, pager & hooks](#26-editor-pager--hooks)
   - 2.7 [Stash hygiene](#27-stash-hygiene)
   - 2.8 [Secret scanning](#28-secret-scanning)
   - 2.9 [Submodules & worktrees](#29-submodules--worktrees)
3. [GitHub CLI (`gh`)](#github-cli-gh)
   - 3.1 [Auth & setup](#31-auth--setup)
   - 3.2 [Token-efficient invocation via `rtk`](#32-token-efficient-invocation-via-rtk)
   - 3.3 [Discovery & defaults](#33-discovery--defaults)
   - 3.4 [Pull request review](#34-pull-request-review)
   - 3.5 [Workflow runs](#35-workflow-runs)
   - 3.6 [`gh api` cheatsheet](#36-gh-api-cheatsheet)
   - 3.7 [Output discipline](#37-output-discipline)
   - 3.8 [Read-only allowance](#38-read-only-allowance)
   - 3.9 [Never without explicit consent](#39-never-without-explicit-consent)
4. [Integration with workspace tools](#integration-with-workspace-tools)
5. [Escalation & troubleshooting](#escalation--troubleshooting)
6. [Change log](#change-log)

---

## Core Principles

1. **Reversibility over speed.** Prefer reversible operations (new commit, dry-run, reflog) over fast destructive ones (`--force`, `--hard`, `clean -f`).
2. **Explicit over implicit.** Stage files by name, ask before mutating remote state, name every script.
3. **Auditability.** Every commit goes through `./.agents/scripts/helper.sh commit`. Every remote mutation requires explicit user consent.
4. **Token efficiency.** Use the `rtk` proxy where available; cap output before printing.
5. **Stricter rule wins.** On conflict between this document and `AGENTS.md` / `project_rules.md` / `git-ops` skill, apply the stricter constraint.

---

## Git

### 2.1 Protected branches

The following branches are **protected**. Destructive operations (`reset --hard`, `push --force`, `branch -D`, `clean -f`, restoring a tracked path from a different ref) require **explicit, in-conversation user approval** before execution.

- `main`, `master`
- `release/*`, `hotfix/*`
- Any branch matching patterns enforced by GitHub branch protection rules or `CODEOWNERS`
- The detected default branch (see §2.2)

When uncertain whether a branch is protected, treat it as protected.

### 2.2 Default-branch detection

Do **not** hardcode `main` or `master`. Use this discovery sequence in scripts (each step falls back to the next on failure):

```bash
# 1. Preferred: query GitHub via `gh` (most reliable).
default_branch=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')

# 2. Fallback: use the local symbolic ref if it exists.
default_branch=$(git symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null | sed 's|^origin/||')

# 3. Last-resort: parse `git remote show`.
default_branch=$(git remote show origin 2>/dev/null | awk '/HEAD branch/ {print $NF}')
```

If all three fail, **halt and ask the user** — do not guess.

### 2.3 Staging discipline

Stage files **explicitly by name**. The two commonly misused commands are not equivalent:

| Command | Scope | Why it is dangerous here |
|---|---|---|
| `git add -A` / `--all` | **Entire working tree**, including deletions | Sweeps up secrets, build artefacts, stray files anywhere in the repo, even outside `cwd` |
| `git add .` | Current directory and subdirectories only | Safer than `-A`, but still sweeps everything under `cwd`. In monorepos with mixed `.gitignore` quality this still catches too much |

```bash
# ✅ Correct — explicit paths, easy to audit
git add src/auth/login.ts src/auth/login.test.ts

# ⚠️ Acceptable only when the whole subdirectory is the intended change AND `.gitignore` is verified
git add src/auth/

# ❌ Avoid in this workspace
git add -A
git add .
```

After staging, **always inspect** with `git diff --cached` before committing — verify no debug statements, secrets, or unrelated edits slipped in. To unstage a stray file: `git restore --staged <path>`.

### 2.4 Destructive operations

| Operation | Safer alternative | When raw op is OK |
|---|---|---|
| `git push --force` | `git push --force-with-lease` (refuses if upstream moved) | Only with explicit user approval AND after `git fetch` confirms the remote ref |
| `git reset --hard` | `git reset --mixed` (keeps working tree) | Only with explicit user approval |
| `git branch -D` | `git branch -d` (refuses if unmerged) | Only after verifying the commits are reachable elsewhere |
| `git clean -fd` | `git clean -nd` (dry-run preview) | Only after the dry-run is reviewed |
| `git checkout <branch> -- <file>` | `git restore --source=<branch> <file>` | Either form is acceptable |

**Workspace-specific note.** `helper.sh push -f` currently uses raw `--force` (not `--force-with-lease`). Until that helper is extended, agents that need safe force-push should bypass `helper.sh push` and call `git push --force-with-lease` directly, with explicit user approval.

Before any destructive op on a non-protected branch:

1. `git fetch` to ensure refs are current.
2. Confirm the operation is on the intended branch (`git branch --show-current`).
3. Confirm the user has approved it in the current conversation.
4. Prefer dry-run flags when they exist (`--dry-run`, `-n`).

### 2.5 Commits & history rewriting

- **Raw `git commit` is forbidden.** Always use `./.agents/scripts/helper.sh commit <type> <scope> "description" [files...]`. The pre-commit hook blocks raw commits. Flags available: `--no-test`, `--no-verify`, `--amend`.
- **Conventional Commits required.** Format: `type(scope): description`. Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `build`, `ci`. Scopes are project-module names (e.g. `auth`, `frontend`, `infra`).
- **Amend policy**:
  - Local commit (not pushed): amending via `helper.sh commit --amend` is fine.
  - Pushed commit, no PR yet: amend allowed, but warn about coordination cost.
  - Published commit (PR exists, others may have based work on it): **create a new commit** instead. Amend requires explicit user approval.
- **Signing.** When the active profile has a signing key (`git config commit.gpgsign` is true), commits are signed automatically. Do not bypass signing with `--no-gpg-sign`.

### 2.6 Editor, pager & hooks

For any non-interactive `git` invocation that may open an editor or pager, set both:

```bash
GIT_EDITOR=true GIT_PAGER=cat git <command>
# or use the global flag
git --no-pager <command>
```

`GIT_EDITOR=true` alone is **not** sufficient — `git log`, `git diff`, `git rebase -i`, and many subcommands open a pager in a TTY. Set `GIT_PAGER=cat` (or `--no-pager`) too.

**Never** bypass hooks with `--no-verify` unless the user explicitly asks. If a hook fails, **fix the underlying issue** — do not silence it.

For `git rebase` / `merge --squash` / similar commands that may spawn an editor, also set:

```bash
GIT_EDITOR=true GIT_PAGER=cat git rebase -i HEAD~3
GIT_SEQUENCE_EDITOR=true git rebase -i ...   # for todo-list editor
```

### 2.7 Stash hygiene

- Always name your stashes: `git stash push -m "WIP: ticket-1234 brief context"`.
- Before popping, confirm the branch is correct: `git stash list` then `git stash show -p stash@{n}` to inspect.
- Pop one branch at a time. Popping the wrong stash onto the wrong branch is a common data-loss scenario.
- For longer-lived work, prefer a worktree (`git worktree add ../sibling-branch <branch>`) over stashing.

### 2.8 Secret scanning

Before staging:

1. Run `git status` and review untracked files. Anything matching `.env*`, `*.key`, `*.pem`, `credentials.*`, `id_rsa*` must **not** be staged.
2. Confirm `.antigravityignore` patterns are honored (per `AGENTS.md` §3).
3. Run `git diff --cached` to confirm no secret literals appear (grep for patterns like `AKIA`, `-----BEGIN`, `ghp_`, `xoxb-`).
4. If a secret was committed: **stop, do not push**. Use `git reset` (if local only) or rotate the credential and `git filter-repo` (if pushed). Escalate immediately.

### 2.9 Submodules & worktrees

- **Submodules.** When updating, prefer `git submodule update --init --recursive`. Never commit inside a submodule from the parent repo.
- **Worktrees.** Useful for parallel work without stashing (`git worktree add ../sibling-branch feat/x`). Clean up with `git worktree remove <path>` when done — do not leave orphaned worktrees.

---

## GitHub CLI (`gh`)

`gh` is the canonical interface for GitHub in this workspace. Prefer it over web scraping, undocumented REST paths, or guesswork.

### 3.1 Auth & setup

```bash
gh auth status                # confirm logged in & scopes
gh auth refresh -s <scope>    # request additional scopes (read:org, workflow, etc.)
gh auth token                 # retrieve token for subshells — do not log or echo
```

If `gh auth status` shows logged out, **halt and ask the user to run `gh auth login`**. Do not attempt interactive login on their behalf.

The repo is inferred from cwd. When invoking `gh` from outside the repo (CI scripts, helper utilities), pass `-R OWNER/REPO` explicitly.

### 3.2 Token-efficient invocation via `rtk`

This workspace ships the `rtk` CLI proxy, which tokenises `gh` output before it reaches the LLM context. **Prefer `rtk gh <cmd>` over raw `gh <cmd>`** for interactive agent work to reduce token usage:

```bash
rtk gh pr view 123          # tokenised PR view
rtk gh run view 456 --log-failed
rtk gh api repos/.../pulls/123 --jq '.title'
```

`rtk gh` does **not** cover every subcommand — for full output (e.g. when debugging tokenisation), fall back to `gh <cmd> -v` or `gh <cmd> --verbose`.

### 3.3 Discovery & defaults

- Discover flags with `gh <cmd> --help` rather than guessing or memorising.
- Set stable defaults once per environment: `gh config set editor <editor>`, `gh config set browser <browser>`, `gh config set pager cat`.
- Useful non-mutating subcommands worth knowing:
  - `gh repo view --json defaultBranchRef,name,owner`
  - `gh search issues|prs|code|commits "<query>" --limit 20` — read-only, safe unprompted
  - `gh workflow view <file|name>`
  - `gh alias set <name> '<cmd>'` — personal shortcuts
  - `gh status` — overview of assigned work

### 3.4 Pull request review

**Top-level review verbs** (single body, no inline comments):

```bash
gh pr review <N> --approve --body "LGTM"
gh pr review <N> --request-changes --body "see comments"
gh pr review <N> --comment --body "questions before approving"
gh pr review <N> --dismiss                            # dismiss stale bot reviews (also a state mutation — see §3.9)
```

**Multi-comment inline review** — there is no `gh pr review` flag for line-anchored multi-comment posts; use the REST API in one review:

```bash
gh api repos/OWNER/REPO/pulls/123/reviews \
  -f event=COMMENT \
  -f body="overall notes" \
  -F 'comments[][path]=src/foo.py' -F 'comments[][line]=42' \
  -F 'comments[][body]=this is wrong because…' \
  -F 'comments[][path]=src/bar.py'  -F 'comments[][line]=17' \
  -F 'comments[][body]=and here…'
```

Constraints:
- Each `(path, line, body)` triple must be unique within the request — duplicate entries are rejected.
- The `line` must reference a line in the PR's final diff (not an outdated line).
- There is no API to edit an inline comment after submission. To respond, reply to the thread (below) or mark the thread obsolete via GraphQL.

**Reply to a specific inline thread**:

```bash
gh api repos/OWNER/REPO/pulls/123/comments/COMMENT_ID/replies -f body="fixed in abc1234"
```

**Resolve a review thread** — requires the GraphQL thread node ID (fetch via `pullRequest.reviewThreads`), then:

```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' \
  -F id=THREAD_NODE_ID
```

**Listing comments** — two endpoints, easy to confuse:

```bash
gh api repos/OWNER/REPO/pulls/123/comments  --paginate   # inline, line-anchored
gh api repos/OWNER/REPO/issues/123/comments --paginate   # PR-level conversation
```

### 3.5 Workflow runs

Default to **failed-only** logs:

```bash
gh run view 123456 --log-failed          # preferred
gh run view 123456 --log | tail -200     # only if --log-failed isn't enough
```

Find the run behind a PR's latest push:

```bash
gh pr checks 123 --json name,state,link,workflow
```

Avoid `gh pr checks --watch` in non-interactive contexts — it blocks until completion.

### 3.6 `gh api` cheatsheet

```bash
-f key=val      # string param
-F key=val      # typed (numbers, booleans, @file)
-X METHOD       # HTTP verb (GET, POST, PATCH, PUT, DELETE)
--jq '.field'   # filter JSON response
--paginate      # follow Link headers
--input <file>  # bulk JSON body
--silent        # suppress status output in scripts
```

Additional tips:
- **Rate limits:** 5,000 REST requests/hour authenticated, GraphQL is cost-based. For bulk operations, prefer GraphQL to amortise cost.
- **For multi-megabyte responses**, write to a file then process: `gh api ... > /tmp/out.json && jq '.field' /tmp/out.json`.
- **GraphQL cost**: check `extensions.cost` in the response to track budget.

### 3.7 Output discipline

Always cap output before printing. Common patterns:

```bash
gh pr diff 123 --name-only                          # list touched files first
gh api repos/.../pulls/123/files --jq '.[].filename'
gh run view 123456 --log-failed | tail -100
gh api ... --paginate --jq '.[] | .name' | head -50
gh search prs "<query>" --json number,title --limit 20 --jq '.[] | "\(.number): \(.title)"'
```

Prefer `--json field1,field2` over post-hoc `--jq` when you know the fields you want — it cuts response size at the source.

### 3.8 Read-only allowance

Read-only commands are safe to run unprompted:

- `gh pr|issue|repo|run|workflow|release|search <sub> list|view|status|diff|checks`
- `gh api <GET>`
- `gh pr checks` (without `--watch`)
- `gh status`

Caveats:
- `gh pr checks --watch` **blocks** — avoid in non-interactive scripts.
- `gh workflow run --web` opens a browser — do not run unless explicitly approved.
- Even read-only-looking commands can have side effects:
  - `gh auth refresh` mutates auth state.
  - `gh repo sync` updates local branches from remote.
  - `gh release download` writes files to disk.

### 3.9 Never without explicit consent

The following **publish, mutate, or notify**. Do **not** run any of these without an explicit in-conversation request from the user. When in doubt, surface the command and wait.

**Pull requests & issues**

- `gh pr review` (any of `--approve`, `--request-changes`, `--comment`, `--dismiss`)
- `gh pr comment`, `gh issue comment`
- `gh pr merge` (any flags, including `--auto`)
- `gh pr close`, `gh pr reopen`, `gh pr ready`, `gh pr ready --undo`, `gh pr edit`
- `gh issue close`, `gh issue reopen`, `gh issue edit`, `gh issue delete`, `gh issue transfer`
- Posts via `gh api .../comments` or `.../reviews` (writing — reading is fine)

**Repositories**

- `gh repo create`, `gh repo edit`, `gh repo archive`, `gh repo delete`
- `gh repo set-default`, `gh repo fork`
- `gh repo sync` (overwrites local refs)

**Releases & artifacts**

- `gh release create`, `gh release edit`, `gh release delete`
- `gh release upload`, `gh release delete-asset`
- `gh attestation sign`

**CI / workflows**

- `gh run rerun`, `gh run cancel`, `gh run delete`
- `gh workflow enable`, `gh workflow disable`

**Secrets & variables**

- `gh secret set`, `gh secret delete`
- `gh variable set`, `gh variable delete`

**Codespaces**

- `gh codespace create`, `gh codespace delete`, `gh codespace stop`

**Gists**

- `gh gist create`, `gh gist edit`, `gh gist delete`

**Projects (v2)**

- `gh project item-add`, `gh project item-archive`, `gh project mark-template`, `gh project close`, `gh project delete`

**Git remote operations** (mirror of §2.4)

- `git push`, `git push --force`, `git push --tags`, deleting remote branches/tags
- `helper.sh push -f` (uses raw `--force` — see §2.4)

**Any HTTP mutation**: `gh api -X POST`, `-X PATCH`, `-X PUT`, `-X DELETE` — including resolving review threads via GraphQL.

---

## Integration with workspace tools

This document does not replace the existing rules — it ties them together.

| Concern | Authoritative doc | This doc adds |
|---|---|---|
| Commit message format, branch isolation | `AGENTS.md` §5–6, `git-ops` SKILL | Safer staging rules (§2.3), `GIT_PAGER` (§2.6), stash hygiene (§2.7) |
| Git profile rotation, `helper.sh commit` enforcement | `AGENTS.md` §6, `project_rules.md` §6 | `--force-with-lease` guidance (§2.4) |
| Workspace scripts | `helper.sh` | Defensive fallback chain for default-branch detection (§2.2) |
| Pre-commit hook gate | `.agents/hooks/pre-commit` | Reminder: never `--no-verify` (§2.6) |
| `.antigravityignore` | `AGENTS.md` §3 | Cross-reference from §2.8 secret scan |
| Token efficiency | (none) | `rtk gh` as preferred invocation path (§3.2) |

**Conflict resolution.** If this doc is stricter than another, follow this doc. If another is stricter, follow that one. Never relax a stricter rule based on a looser source.

**Bootstrap reminder.** Before any code mutation, the canonical sequence is:

```bash
./.agents/scripts/helper.sh validate   # sync gate
./.agents/scripts/helper.sh doctor     # diagnostic
./.agents/scripts/helper.sh issue checkout <id>   # create/switch branch
# ... edits ...
./.agents/scripts/helper.sh validate   # pre-commit gate
./.agents/scripts/helper.sh commit <type> <scope> "desc" <files...>
```

---

## Escalation & troubleshooting

| Symptom | First action |
|---|---|
| `gh auth status` shows logged out | Ask user to run `gh auth login` — never attempt interactive login on their behalf |
| REST API returns 403 / rate limited | Check `gh api /rate_limit`; switch to GraphQL to amortise; back off and retry |
| GraphQL "Field doesn't exist" | Verify the schema version; some fields require preview headers |
| `git push` rejected (protected branch) | Stop. Confirm with user whether they want to override via the GitHub UI flow |
| Hook fails on commit | Read the hook output, fix the underlying issue, do not use `--no-verify` |
| Branch gone after rebase | `git reflog` to find the lost commits, recreate the branch |
| Merge conflict | Halt and notify the user — do not auto-resolve |
| `helper.sh push -f` would be safer as `--force-with-lease` | Bypass the helper once, call `git push --force-with-lease` directly with user approval; log the gap |
| Unsure if a `gh` command mutates | Check this doc §3.9; if not listed, `gh <cmd> --help` will reveal write-side flags; when still unsure, ask the user |

When a decision is required that the agent cannot make safely, **flag it through the local issue tracker** (`./.agents/scripts/helper.sh issue create`) rather than guessing.

---

## Change log

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-06-17 | Initial consolidated version. Replaces scattered guidance previously implied across `AGENTS.md`, `git-ops` skill, and ad-hoc instructions. Adds: `rtk gh` token-efficiency guidance, safer `git add` distinction, `--force-with-lease` alternatives, complete `gh` mutating-subcommand inventory, fallback chain for default-branch detection, troubleshooting matrix. |
