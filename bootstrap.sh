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
# AGENTS.md — <Project Name>

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand.

## 1. What this project is
- **Product:** <one-line description>
- **Stack:** General Project
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
- **NEVER** commit secrets, `.env*` files, or credentials.
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first.

## 3. Context map — what loads when
| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, rules, map | Always |
| `.agents/skills/*/SKILL.md` | Playbooks | On demand |
| `.agents/tasks/board.md` | Task board | Read at start, written at change |
| `.agents/memory/architecture.md` | System summary | On demand |

## 4. Working protocol
1. **Before coding:** Read `.agents/tasks/board.md`.
2. **Before any architecture-affecting change:** check `.agents/memory/decisions/` for a relevant ADR.
EOF
  echo "Created AGENTS.md template."
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
