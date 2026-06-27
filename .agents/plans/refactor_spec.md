# Refactor Specification: CLI, Validation Guard, and Git API

We have aligned on a comprehensive refactoring and bugfix plan for the core components of the AAC V2 system.

## 1. Validation Guard (`validate.py`)
We will refactor this script to improve modularity, execution speed, and usability:
- **Modularity**: Extract each of the 8 validation checks into distinct Python functions (e.g. `audit_critical_files()`, `audit_secrets()`, `audit_link_integrity()`, etc.).
- **Performance Optimization**: Exclude heavy/build directories like `dist`, `build`, `out`, and `.next` from the secret scanner's fallback walker to ensure fast execution on larger projects.
- **Ignore File Compliance**: Check staged files against patterns in `.gitignore` (using `git check-ignore`) and `.antigravityignore` (using a regex conversion helper) to ensure ignored files are not staged or committed.
- **Audit Summary Table**: Build a clean visual status grid at the end of the script displaying the final pass/fail status of each audit step (resembling a checklist).

## 2. CLI Dispatcher (`helper.py` & commands)
We will improve CLI robustness:
- **Clean Argument Parsing**: Refactor CLI commands to check arguments defensively and use return values rather than calling raw `sys.exit` directly inside low-level helpers where possible.
- **Dynamic Command Dispatching**: Clean up dynamic import and path verification inside [helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py).

## 3. GitHub API Client (`git_api.py` & `issue.py`)
We will resolve bugs and warning visibility issues:
- **Bearer Authentication**: Update GITHUB API headers to use the modern `Bearer {token}` authorization format.
- **Robust Git remote parsing**: Implement robust URL pattern matching in `get_repo_info()` to properly parse SSH and HTTPS git remotes.
- **Detailed Log Warnings**: Ensure [git_api.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/git_api.py) prints clear warnings if the `GITHUB_TOKEN` is not set or if the repository remote `origin` is missing, allowing users to understand why GitHub integration was bypassed.

---

## 4. Implementation Subtasks

1. **Refactor validate.py**: Restructure the script into 8 modular functions, add the summary box printer, update exclude directories, and implement strict `.gitignore` and `.antigravityignore` staged file validation checks.
2. **Refactor git_api.py**: Apply API headers, improve remote URL parsing, and add missing configurations warning logs.
3. **Refactor helper.py**: Streamline CLI path resolving and command dispatching.
4. **Refactor issue.py**: Check `git_api` returns and print warning logs to the user if GitHub issue creation was bypassed due to missing tokens or remote setup.
5. **Run Unit Tests**: Execute `python3 -m unittest discover` to ensure all tests pass.
