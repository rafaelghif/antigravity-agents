#!/usr/bin/env bash
# Antigravity Agent Core Helper Script
set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
ARCHIVE_DIR=".agents/archive"

show_help() {
    echo "Usage: \$0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  init [name] [stack] [arch] Initialize the workspace interactively or with parameters"
    echo "  recon             Run autonomous codebase stack and directory structure detection"
    echo "  validate          Perform security audit, lock checks, and memory size validation"
    echo "  doctor            Diagnose workspace health and verify system executables"
    echo "  commit            Verify code tests, run security checks, and execute conventional commit"
    echo "  sync-git          Synchronize Git branch and last commit hash with memory.md"
    echo "  lock [module]     Acquire a lock on a module"
    echo "  unlock [module]   Release a lock on a module"
    echo "  archive           Archive completed sprint tasks and reset memory.md checklist"
    echo "  help              Show this help message"
}

cmd_sync_git() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local commit
    commit=$(git log -n 1 --format="%h" 2>/dev/null || echo "none")

    # Update memory.md using sed
    sed -i -E "s|- \*\*Active Branch\*\*: .*|- **Active Branch**: $branch|" "$MEMORY_FILE"
    sed -i -E "s|- \*\*Last Commit Reference\*\*: .*|- **Last Commit Reference**: $commit|" "$MEMORY_FILE"
    echo "Synchronized: Branch=$branch, Commit=$commit in $MEMORY_FILE"
}

cmd_lock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to lock." >&2
        exit 1
    fi
    mkdir -p "$LOCKS_DIR"
    local lockfile="$LOCKS_DIR/$module.lock"
    if [ -f "$lockfile" ]; then
        echo "Error: Module '$module' is already locked!" >&2
        cat "$lockfile" >&2
        exit 1
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat << INNER_EOF > "$lockfile"
Branch: $branch
Owner: Agent
Timestamp: $timestamp
INNER_EOF
    echo "Acquired lock for module '$module' at $lockfile"
}

cmd_unlock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to unlock." >&2
        exit 1
    fi
    local lockfile="$LOCKS_DIR/$module.lock"
    if [ ! -f "$lockfile" ]; then
        echo "Warning: Module '$module' is not locked." >&2
        exit 0
    fi
    rm -f "$lockfile"
    echo "Released lock for module '$module'"
}

cmd_archive() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    mkdir -p "$ARCHIVE_DIR"
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    # replace slashes in branch name to avoid path issues
    branch_clean=${branch//\//_}
    local archive_file="$ARCHIVE_DIR/sprint_${branch_clean}.md"

    echo "Archiving tasks to $archive_file..."
    
    # Extract checklist from memory.md
    sed -n '/### Sprint Tasks Checklist/,/---/p' "$MEMORY_FILE" | grep -v '---' > "$archive_file"

    # Relocate workflow and PR review files to a branch-specific subdirectory
    local branch_archive_dir="$ARCHIVE_DIR/sprint_${branch_clean}"
    mkdir -p "$branch_archive_dir"
    echo "Archiving workflow and PR review files to $branch_archive_dir..."
    find .agents/workflows -maxdepth 1 -name "task_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true
    find .agents/workflows -maxdepth 1 -name "pr_review_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true


    # Reset checklist in memory.md
    local start_line
    start_line=$(grep -n "### Sprint Tasks Checklist" "$MEMORY_FILE" | cut -d: -f1)
    if [ -z "$start_line" ]; then
        echo "Error: Could not locate checklist section in $MEMORY_FILE" >&2
        exit 1
    fi

    local end_line
    end_line=$(tail -n +$start_line "$MEMORY_FILE" | grep -n "^---" | head -n 1 | cut -d: -f1)
    if [ -z "$end_line" ]; then
        end_line=$(wc -l < "$MEMORY_FILE")
    else
        end_line=$((start_line + end_line - 1))
    fi

    local temp_file
    temp_file=$(mktemp)
    head -n "$start_line" "$MEMORY_FILE" > "$temp_file"
    cat << 'INNER_EOF' >> "$temp_file"
- [ ] Implement core logic
- [ ] Write unit tests
- [ ] Verify build and tests pass
INNER_EOF
    tail -n +"$end_line" "$MEMORY_FILE" >> "$temp_file"
    mv "$temp_file" "$MEMORY_FILE"
    echo "Checklist reset successfully."
}

cmd_init() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Initialization"
    echo "=========================================================="
    
    local project_name="${2:-}"
    local tech_stack="${3:-}"
    local arch_pattern="${4:-}"
    local db_orm="${5:-}"
    local env_vars="${6:-}"
    local scaffold=""

    if [ -z "$project_name" ]; then
        read -p "Enter Project Name (default: My Project): " project_name
        if [ -z "$project_name" ]; then project_name="My Project"; fi
    fi
    
    if [ -z "$tech_stack" ]; then
        read -p "Enter Language/Framework (e.g. Node/TypeScript, Go, Python) (default: Node/TypeScript): " tech_stack
        if [ -z "$tech_stack" ]; then tech_stack="Node/TypeScript"; fi
    fi

    if [ -z "$arch_pattern" ]; then
        read -p "Enter Architectural Pattern (e.g. Clean, MVC, Hexagonal) (default: MVC): " arch_pattern
        if [ -z "$arch_pattern" ]; then arch_pattern="MVC"; fi
    fi

    if [ -z "$db_orm" ]; then
        read -p "Enter Database/ORM (e.g. Prisma, PostgreSQL, None) (default: None): " db_orm
        if [ -z "$db_orm" ]; then db_orm="None"; fi
    fi

    if [ -z "$env_vars" ]; then
        read -p "Enter config variables (comma-separated, e.g. PORT,DATABASE_URL) (default: None): " env_vars
        if [ -z "$env_vars" ]; then env_vars=""; fi
    fi

    if [ -z "${7:-}" ]; then
        read -p "Scaffold initial project folders? (y/n) (default: y): " scaffold
        if [ -z "$scaffold" ]; then scaffold="y"; fi
    else
        scaffold="${7:-}"
    fi

    # Initialize Git if not present
    if [ ! -d .git ]; then
        echo "Initializing Git repository..."
        git init
        git branch -m main
    fi

    # Install Git post-commit Hook template
    if [ -f .agents/hooks/post-commit ]; then
        mkdir -p .git/hooks
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "Git post-commit hook installed."
    fi

    # Scaffolding folders if requested
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "yes" ]; then
        echo "Scaffolding directory structure..."
        mkdir -p src tests config
        
        # Node/TypeScript Template
        if [[ "$tech_stack" =~ "Node" || "$tech_stack" =~ "TypeScript" || "$tech_stack" =~ "TS" ]]; then
            if [ ! -f package.json ]; then
                cat << 'JSON_EOF' > package.json
{
  "name": "project",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint 'src/**/*.ts'"
  },
  "dependencies": {},
  "devDependencies": {}
}
JSON_EOF
                echo "Created package.json scaffolding"
            fi
        fi
        
        # Go Template
        if [[ "$tech_stack" =~ "Go" || "$tech_stack" =~ "Golang" ]]; then
            if [ ! -f go.mod ]; then
                cat << 'GO_EOF' > go.mod
module project

go 1.20
GO_EOF
                echo "Created go.mod scaffolding"
            fi
            if [ ! -f src/main.go ]; then
                cat << 'GO_EOF' > src/main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Antigravity!")
}
GO_EOF
                echo "Created src/main.go template"
            fi
        fi

        # Python Template
        if [[ "$tech_stack" =~ "Python" || "$tech_stack" =~ "Py" ]]; then
            if [ ! -f src/main.py ]; then
                cat << 'PY_EOF' > src/main.py
def main():
    print("Hello, Antigravity!")

if __name__ == "__main__":
    main()
PY_EOF
                echo "Created src/main.py template"
            fi
        fi
    fi

    # Create .env and .env.example if env_vars exist
    if [ -n "$env_vars" ]; then
        echo "Writing configuration environment variables..."
        IFS=',' read -ra ADDR <<< "$env_vars"
        # Reset files
        > .env.example
        > .env
        for i in "${ADDR[@]}"; do
            echo "$i=" >> .env.example
            echo "$i=" >> .env
        done
        echo "Created .env and .env.example templates"
    fi

    # Run auto-recon to generate the blueprints
    echo "Running autonomous reconnaissance to populate blueprint files..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh
    fi

    echo "=========================================================="
    echo "Workspace initialized successfully for '$project_name'!"
    echo "=========================================================="
}

cmd_recon() {
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh
    else
        echo "Error: recon.sh not found at .agents/scripts/recon.sh" >&2
        exit 1
    fi
}

cmd_validate() {
    if [ -f .agents/scripts/validate.sh ]; then
        .agents/scripts/validate.sh
    else
        echo "Error: validate.sh not found at .agents/scripts/validate.sh" >&2
        exit 1
    fi
}

cmd_doctor() {
    echo "=========================================================="
    echo "  Antigravity Workspace Doctor Diagnostics"
    echo "=========================================================="
    
    local errors=0
    
    # Check Git Repository
    if [ -d .git ]; then
        echo "  [PASS] Git repository initialized."
    else
        echo "  [FAIL] Git repository not initialized!"
        errors=$((errors + 1))
    fi
    
    # Check post-commit hook
    if [ -f .git/hooks/post-commit ] && [ -x .git/hooks/post-commit ]; then
        echo "  [PASS] post-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git post-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit"
    fi
    
    # Check helper script executability
    if [ -x .agents/scripts/helper.sh ]; then
        echo "  [PASS] helper.sh is executable."
    else
        echo "  [WARNING] helper.sh is not executable."
        chmod +x .agents/scripts/helper.sh
    fi
    
    # Check recon script
    if [ -f .agents/scripts/recon.sh ]; then
        if [ -x .agents/scripts/recon.sh ]; then
            echo "  [PASS] recon.sh is executable."
        else
            echo "  [WARNING] recon.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/recon.sh
        fi
    else
        echo "  [FAIL] recon.sh is missing!"
        errors=$((errors + 1))
    fi

    # Check validate script
    if [ -f .agents/scripts/validate.sh ]; then
        if [ -x .agents/scripts/validate.sh ]; then
            echo "  [PASS] validate.sh is executable."
        else
            echo "  [WARNING] validate.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/validate.sh
        fi
    else
        echo "  [FAIL] validate.sh is missing!"
        errors=$((errors + 1))
    fi

    # Run validate.sh checks
    if [ -f .agents/scripts/validate.sh ]; then
        echo "----------------------------------------------------------"
        if ! .agents/scripts/validate.sh; then
            errors=$((errors + 1))
        fi
    fi
    
    echo "=========================================================="
    if [ $errors -eq 0 ]; then
        echo "Doctor diagnostics: ALL SYSTEMS HEALTHY"
        exit 0
    else
        echo "Doctor diagnostics: FOUND $errors ERROR(S) / WARNING(S)"
        exit 1
    fi
}

cmd_commit() {
    local no_test_flag="false"
    local stage_files=()
    local type=""
    local scope=""
    local desc=""

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-test|--no-verify)
                no_test_flag="true"
                shift
                ;;
            *)
                if [ "$1" = "commit" ]; then
                    shift
                elif [ -z "$type" ]; then
                    type="$1"
                    shift
                elif [ -z "$scope" ]; then
                    scope="$1"
                    shift
                elif [ -z "$desc" ]; then
                    desc="$1"
                    shift
                else
                    stage_files+=("$1")
                    shift
                fi
                ;;
        esac
    done

    # Interactive inputs if parameters are missing
    if [ -z "$type" ]; then
        echo "Choose commit type:"
        echo "  [1] feat:     A new feature"
        echo "  [2] fix:      A bug fix"
        echo "  [3] refactor: A code change that neither fixes a bug nor adds a feature"
        echo "  [4] chore:    Changes to the build process or auxiliary tools and libraries"
        echo "  [5] docs:     Documentation only changes"
        echo "  [6] test:     Adding missing tests or correcting existing tests"
        echo "  [7] perf:     A code change that improves performance"
        read -p "Select number or type string (default: feat): " type_choice
        case "$type_choice" in
            1) type="feat" ;;
            2) type="fix" ;;
            3) type="refactor" ;;
            4) type="chore" ;;
            5) type="docs" ;;
            6) type="test" ;;
            7) type="perf" ;;
            "") type="feat" ;;
            *) type="$type_choice" ;;
        esac
    fi

    if [ -z "$scope" ]; then
        read -p "Enter commit scope (e.g. core, auth, db, shared) (default: core): " scope
        if [ -z "$scope" ]; then scope="core"; fi
    fi

    if [ -z "$desc" ]; then
        read -p "Enter brief description of change: " desc
        if [ -z "$desc" ]; then
            echo "Error: Description cannot be empty." >&2
            exit 1
        fi
    fi

    # Workspace Validation
    echo "Running workspace validation checks..."
    if ! .agents/scripts/validate.sh; then
        echo "Error: Workspace validation failed. Aborting commit." >&2
        exit 1
    fi

    # Linter Execution
    if [ "$no_test_flag" = "false" ]; then
        local linter_cmd=""
        if [ -f .agents/project_rules.md ]; then
            linter_cmd=$(grep "Linter command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
        fi

        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            echo "Running linter command: $linter_cmd..."
            if ! eval "$linter_cmd"; then
                echo "Error: Linter check failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] Linter check passed successfully."
        else
            echo "No linter configured in project_rules.md. Skipping linting."
        fi
    else
        echo "Linter check bypassed via --no-test / --no-verify."
    fi

    # Test Execution
    if [ "$no_test_flag" = "false" ]; then
        local test_runner=""
        if [ -f .agents/project_rules.md ]; then
            test_runner=$(grep "Test runner command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
        fi

        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            echo "Running test suite: $test_runner..."
            if ! eval "$test_runner"; then
                echo "Error: Test runner suite failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] All tests passed successfully."
        else
            echo "No test runner configured in project_rules.md. Skipping tests."
        fi
    else
        echo "Test execution bypassed via --no-test / --no-verify."
    fi

    # File Staging
    if [ ${#stage_files[@]} -gt 0 ]; then
        echo "Staging specified files: ${stage_files[*]}..."
        git add "${stage_files[@]}"
    else
        echo "Staging all modified and untracked files..."
        # Check if there are changes to stage
        if [ -n "$(git status --porcelain | grep -v '^\?\? .agents/locks/')" ]; then
            git add -A -- ':!.agents/locks/*'
        fi
    fi

    # Conventional Commit Execution
    local commit_msg="$type($scope): $desc"
    echo "Executing conventional commit: '$commit_msg'..."
    if git commit -m "$commit_msg"; then
        echo "Commit successful."
    else
        echo "Error: Git commit failed." >&2
        exit 1
    fi
}

# Dispatch command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

case "$1" in
    init)
        cmd_init "$@"
        ;;
    recon)
        cmd_recon
        ;;
    validate)
        cmd_validate
        ;;
    doctor)
        cmd_doctor
        ;;
    commit)
        cmd_commit "$@"
        ;;
    sync-git)
        cmd_sync_git
        ;;
    lock)
        cmd_lock "${2:-}"
        ;;
    unlock)
        cmd_unlock "${2:-}"
        ;;
    archive)
        cmd_archive
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_help
        exit 1
        ;;
esac
