#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "   Bootstrapping Antigravity Agent Core (AAC) V2...   "
echo "=========================================================="

# 1. Create directories
mkdir -p .agents/memory/decisions
mkdir -p .agents/tasks
mkdir -p .agents/issues
mkdir -p .agents/skills/review
mkdir -p .agents/skills/adr-writer
mkdir -p .agents/skills/debugging
mkdir -p .agents/skills/world-class-programmer
mkdir -p .agents/workflows
mkdir -p .agents/scripts

# 2. Write base files inline if they do not exist
if [ ! -f "AGENTS.md" ]; then
  cat << 'EOF' > AGENTS.md
# AGENTS.md — Antigravity Agent Core (AAC) V2

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand — see the context map below.

## 1. What this project is
- **Product:** Antigravity Agent Core (AAC) V2 — a highly optimized, project-agnostic operational workspace layout and developer protocol designed specifically for agentic coding, prompt caching, and context insulation.
- **Version:** 2.1.0
- **Stack:** Python 3
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
*(Listed first and emphasized — the model weights early, ALWAYS/NEVER-style rules more reliably than buried prose.)*

- **NEVER** commit secrets, `.env*` files, or credentials. Use the secrets approach documented in `.agents/memory/architecture.md`.
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work, and update it when status changes.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first — supersede an old one, don't duplicate it.
- **ALWAYS** use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`) with the task ID in the body.
- **NEVER** run or write raw CLI scripts directly in the workspace root; keep them organized in target directories.
- **ALWAYS** register any new custom skills in their respective subdirectory with a `SKILL.md`.
- **ALWAYS** acquire locks on modules before beginning edits to avoid conflicting parallel modifications.
- **ALWAYS** run `.agents/scripts/validate.py` locally and verify it passes before proposing commits or pull requests.
- **ALWAYS** align your git branch name with an active issue ID and verify a matching issue file exists under `.agents/issues/` (e.g. branch `feat/issue-12` aligns with `.agents/issues/issue_12.md`).
- **ALWAYS** strictly conform to the schemas defined in `.agents/schema.md` when modifying database models or API contracts.
- **NEVER** write to or rely on global configurations outside the project directory (e.g., in user home directory). Everything must be stored strictly within the workspace level under `.agents/` and tracked in git to ensure multi-developer environment consistency.
- **ALWAYS** copy `.agents/git_profiles.example` to `.agents/git_profiles.json` during environment initialization to set up local identity rotation, and verify the `.json` file is never staged or committed.

## 3. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, non-negotiables, map | Always — every prompt |
| `.agents/skills/adr-writer/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/debugging/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/security-audit/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/tasking/SKILL.md` | Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/world-class-programmer/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand, referenced from architecture.md and the `adr-writer` skill — never auto-loaded |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.md` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |

If you're about to paste a paragraph of explanation into this file, it almost certainly belongs in a skill or memory file instead, pulled in with `@path` only when needed. That's what keeps the per-prompt token cost flat as the project grows.

## 4. Working protocol
1. **Fresh Workspace Initialization:** If starting in a completely empty project directory, the agent MUST immediately execute `./helper.sh bootstrap` to interactively setup the project name, stack (Python, Node, PHP), architecture blueprint (`schema.md`), and task board before writing any code.
2. **Before coding:** read `.agents/tasks/board.md`, claim the task, move it to `Doing`.
3. **Pre-Implementation:** Perform a Pre-Implementation Impact Analysis comparing at least two options (following the `world-class-programmer` playbook) to evaluate long-term maintenance and UI/UX simplicity.
4. **Before any architecture-affecting change:** pull `@.agents/memory/architecture.md` and check `.agents/memory/decisions/` for a relevant ADR.
5. **While working:** prefer invoking an existing skill over re-deriving a workflow from scratch.
6. **Before marking a task `Completed`:** tests pass, board updated with implementation notes, and — if the change was architecturally significant — a new or superseding ADR exists (`adr-writer` skill).
7. **End of session:** run `/sync-memory` to fold session learnings into memory and prune anything stale (see `.agents/workflows/sync-memory.md`).

## 5. Git & review
- Branches: `feat/<task-id>-slug`, `fix/<task-id>-slug`.
- One task = one PR where practical; link the task ID in the PR description.
- No self-merging architecturally significant PRs — a second reviewer (human or the `code-review` skill) signs off first.

## 6. Tool permissions
Default to `request-review` in `agy config` for this repo (pauses before destructive/file-write actions). Reserve `proceed-in-sandbox` for disposable environments only. Never set `always-proceed` on a repo with reachable production credentials.

## 7. Maintaining this file
Reviewed like code. Budget: stay under ~150 lines. If it grows past that, move the newest, least-universal addition into a skill or memory file and leave a one-line pointer here instead.
EOF
  echo "Created AGENTS.md template."
else
  # Synchronize Version if AGENTS.md exists
  if command -v python3 &>/dev/null; then
    python3 -c '
import re, os
with open("AGENTS.md", "r", encoding="utf-8") as f:
    content = f.read()
if "- **Version:**" in content:
    content = re.sub(r"-\s+\*\*Version:\*\*.*", "- **Version:** 2.1.0", content)
else:
    content = re.sub(r"(-\s+\*\*Product:\*\*.*)", r"\1\n- **Version:** 2.1.0", content)
with open("AGENTS.md", "w", encoding="utf-8") as f:
    f.write(content)
'
    echo "Synchronized AGENTS.md version."
  fi
fi

if [ ! -f ".agents/rules.md" ]; then
  cat << 'EOF' > .agents/rules.md
# Project Rules
Use **General Project** for the main product stack.
- test command is: `N/A`.
EOF
  echo "Created .agents/rules.md template."
fi

if [ ! -f ".agents/tasks/board.md" ]; then
  cat << 'EOF' > .agents/tasks/board.md
# Task Board
## Todo
- [ ] Initialize project codebase
## Doing
## Done
EOF
  echo "Created .agents/tasks/board.md template."
fi

# 3. Create recon.py if missing (or overwrite with latest version)
cat << 'EOF' > .agents/scripts/recon.py
import os
import re
import sys

def scan_workspace():
    detected_stack = []
    build_tool = None
    test_command = "N/A"
    lint_command = "N/A"
    build_command = "N/A"
    
    has_py = False
    has_js = False
    has_go = False
    has_rs = False
    has_java = False
    has_docker = False
    has_prisma = False
    has_php = False
    has_laravel = False
    has_tailwind = False
    has_css = False
    has_html = False
    has_dotnet = False
    
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', '.pytest_cache', 'vendor'}
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file == 'package.json':
                has_js = True
            elif file.endswith('.py'):
                has_py = True
            elif file == 'go.mod':
                has_go = True
            elif file == 'Cargo.toml':
                has_rs = True
            elif file in ('pom.xml', 'build.gradle', 'build.gradle.kts'):
                has_java = True
            elif file in ('Dockerfile', 'docker-compose.yml'):
                has_docker = True
            elif 'prisma' in file.lower() or 'schema.prisma' in file:
                has_prisma = True
            elif file == 'composer.json' or file.endswith('.php'):
                has_php = True
                if file == 'artisan':
                    has_laravel = True
            elif 'tailwind.config' in file:
                has_tailwind = True
            elif file.endswith(('.css', '.scss', '.sass')):
                has_css = True
            elif file.endswith('.html'):
                has_html = True
            elif file.endswith(('.csproj', '.sln')):
                has_dotnet = True
                
    if has_js:
        detected_stack.append("JavaScript/TypeScript (Node.js)")
        build_tool = "npm"
        test_command = "npm run test"
        lint_command = "npm run lint"
        build_command = "npm run build"
    if has_py:
        detected_stack.append("Python 3")
        if test_command == "N/A":
            test_command = "pytest"
            lint_command = "flake8 ."
            build_command = "pip install -r requirements.txt"
    if has_go:
        detected_stack.append("Go (Golang)")
        test_command = "go test ./..."
        lint_command = "golangci-lint run"
        build_command = "go build"
    if has_rs:
        detected_stack.append("Rust")
        test_command = "cargo test"
        lint_command = "cargo clippy"
        build_command = "cargo build"
    if has_java:
        detected_stack.append("Java/Kotlin")
        test_command = "mvn test"
        build_command = "mvn clean package"
    if has_php:
        if has_laravel:
            detected_stack.append("PHP (Laravel)")
            test_command = "php artisan test"
            build_command = "composer install && php artisan migrate"
        else:
            detected_stack.append("PHP")
            test_command = "./vendor/bin/phpunit"
            build_command = "composer install"
    if has_tailwind:
        detected_stack.append("Tailwind CSS")
    if has_css and not has_tailwind:
        detected_stack.append("CSS3")
    if has_html and not (has_js or has_php or has_py or has_go):
        detected_stack.append("HTML5 (Static Web)")
    if has_dotnet:
        detected_stack.append(".NET (C#)")
        test_command = "dotnet test"
        build_command = "dotnet build"
    if has_docker:
        detected_stack.append("Docker")
    if has_prisma:
        detected_stack.append("Prisma ORM")

    # Defaults if nothing is found
    if not detected_stack:
        detected_stack.append("General Project")
        
    return {
        "stack": ", ".join(detected_stack),
        "build_tool": build_tool,
        "test_command": test_command,
        "lint_command": lint_command,
        "build_command": build_command
    }

def update_agents_md(scan_results):
    agents_file = 'AGENTS.md'
    if not os.path.exists(agents_file):
        print(f"Warning: {agents_file} not found.")
        return

    with open(agents_file, 'r', encoding='utf-8') as f:
        content = f.read()

    stack_pattern = r'(-\s+\*\*Stack:\*\*)\s+.*'
    replacement = f'\\1 {scan_results["stack"]}'
    new_content = re.sub(stack_pattern, replacement, content)

    with open(agents_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated AGENTS.md with detected stack.")

def update_rules_md(scan_results):
    rules_file = '.agents/rules.md'
    if not os.path.exists(rules_file):
        print(f"Warning: {rules_file} not found.")
        return

    with open(rules_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'Use \*\*.*?\*\* (?:for the main product stack|for all CLI scripting)\.?', f'Use **{scan_results["stack"]}** for the main product stack.', content)
    content = re.sub(r'test command is: `.*?`\.|test command before.*', f'test command is: `{scan_results["test_command"]}`.', content)
    
    with open(rules_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated .agents/rules.md with build and test guidelines.")

if __name__ == '__main__':
    print("Running enterprise auto-reconnaissance scan...")
    results = scan_workspace()
    print(f"Detected Stack: {results['stack']}")
    print(f"Recommended Test: {results['test_command']}")
    
    update_agents_md(results)
    update_rules_md(results)
    print("Auto-reconnaissance completed successfully!")
EOF

# 4. Trigger auto-reconnaissance
if command -v python3 &>/dev/null; then
  python3 .agents/scripts/recon.py
else
  echo "Warning: python3 not found. Please run .agents/scripts/recon.py manually after installing python3."
fi

# 5. Set up local Git hooks
if [ -d ".git" ]; then
  # Pre-commit Hook
  cat << 'EOF' > .git/hooks/pre-commit
#!/usr/bin/env bash
if command -v python3 &>/dev/null; then
  python3 .agents/scripts/validate.py
else
  echo "Warning: python3 not found. Skipping commit validation check."
fi
EOF
  chmod +x .git/hooks/pre-commit
  echo "Installed local Git pre-commit hook."

  # Commit-msg Hook
  cat << 'EOF' > .git/hooks/commit-msg
#!/usr/bin/env bash
COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
CONVENTIONAL_REGEX="^(feat|fix|chore|refactor|docs|test|style|perf|ci)(\([a-z0-9_-]+\))?: .+"

if [[ ! "$COMMIT_MSG" =~ $CONVENTIONAL_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Non-compliant commit message format!"
  echo "=========================================================="
  echo "Commit messages must follow Conventional Commits standard:"
  echo "  Format: <type>(<scope>): <subject>"
  echo "  Example: feat(auth): add login endpoint"
  echo "=========================================================="
  exit 1
fi

ID_REGEX="(task-|issue-|chore-)[a-zA-Z0-9_-]+"
if [[ ! "$COMMIT_MSG" =~ $ID_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Missing Task/Issue ID reference!"
  echo "=========================================================="
  echo "Commit messages must include an active task or issue ID reference."
  echo "  Example body: Task ID: issue-123"
  echo "=========================================================="
  exit 1
fi
EOF
  chmod +x .git/hooks/commit-msg
  echo "Installed local Git commit-msg hook."
fi

echo "=========================================================="
echo "   AAC V2 Bootstrap Completed Successfully!             "
echo "=========================================================="
