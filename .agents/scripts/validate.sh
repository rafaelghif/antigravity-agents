#!/usr/bin/env bash
# Antigravity Agent Core - Workspace & Security Validator
# Validates workspace rules, scans for credentials, checks memory size, and details active locks.

set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
PROJECT_RULES=".agents/project_rules.md"

echo "=========================================================="
echo "Starting Antigravity Agent Workspace Validation..."
echo "=========================================================="

FAILED=0

# 1. Check Active Memory Size
if [ -f "$MEMORY_FILE" ]; then
    LINE_COUNT=$(wc -l < "$MEMORY_FILE" | tr -d ' ')
    echo "Check 1: Memory File Line Count: $LINE_COUNT lines"
    if [ "$LINE_COUNT" -gt 100 ]; then
        echo "  [WARNING] Memory file '$MEMORY_FILE' exceeds the 100-line limit ($LINE_COUNT lines)!"
        echo "            Please run './.agents/scripts/helper.sh archive' to compact your memory."
    else
        echo "  [PASS] Memory file size is within recommended limits."
    fi
else
    echo "  [FAIL] Memory file '$MEMORY_FILE' does not exist!"
    FAILED=1
fi

# 2. Check Active Lockfiles
echo "Check 2: Active Module Locks"
if [ -d "$LOCKS_DIR" ] && [ "$(ls -A "$LOCKS_DIR")" ]; then
    echo "  Found active locks:"
    for lock in "$LOCKS_DIR"/*.lock; do
        if [ -f "$lock" ]; then
            mod=$(basename "$lock" .lock)
            echo "  - Module '$mod':"
            sed 's/^/    /' "$lock"
        fi
    done
else
    echo "  [PASS] No active locks found."
fi

# 3. Secret and Credential Scanning (Pre-commit / Validation)
echo "Check 3: Hardcoded Credentials Scan (excluding .agents/ and .git/)"
SECRET_FOUND=0
# Search for API keys, secrets, private keys, passwords
# Match common secret variables and high entropy patterns
SECRET_PATTERNS=("apikey" "api_key" "secret" "password" "passwd" "private_key" "jwt_secret")
FILES_TO_SCAN=$(find . -type f \
    -not -path '*/.*' \
    -not -path './.agents/*' \
    -not -path './node_modules/*' \
    -not -path './dist/*' \
    -not -path './build/*' \
    -not -name 'bootstrap.sh' \
    -not -path '*.md' \
    -not -path '*.json' \
    -not -path '*.lock' \
    -not -path '*.png' \
    -not -path '*.jpg' \
    -not -path '*.gif' 2>/dev/null || true)

if [ -n "$FILES_TO_SCAN" ]; then
    for pattern in "${SECRET_PATTERNS[@]}"; do
        # search for assignment of secrets like API_KEY = "xxx"
        # avoid false positives by ensuring there is an assignment with quotation marks
        res=$(echo "$FILES_TO_SCAN" | xargs grep -rnEi "$pattern\s*=\s*['\"][a-zA-Z0-9_\-\.]{8,}['\"]" 2>/dev/null || true)
        if [ -n "$res" ]; then
            echo "  [FAIL] Potential hardcoded credential found for pattern '$pattern':"
            echo "$res" | sed 's/^/    /'
            SECRET_FOUND=1
        fi
    done
    
    # Scan for RSA/PEM private key headers
    private_key_res=$(echo "$FILES_TO_SCAN" | xargs grep -rn "BEGIN PRIVATE KEY" 2>/dev/null || true)
    if [ -n "$private_key_res" ]; then
        echo "  [FAIL] Hardcoded Private Key Block found:"
        echo "$private_key_res" | sed 's/^/    /'
        SECRET_FOUND=1
    fi
fi

if [ "$SECRET_FOUND" -eq 0 ]; then
    echo "  [PASS] No hardcoded credentials detected in scan scope."
else
    FAILED=1
fi

# 4. Check for Raw Environment Variable Reads
echo "Check 4: Raw Environment Access Scan (domain-purity verification)"
RAW_ENV_FOUND=0
# Scanning JS/TS, Go, Python files for raw env variable access
JS_FILES=$(find . -name "*.js" -o -name "*.ts" -o -name "*.tsx" -not -path './.agents/*' -not -path './node_modules/*' -not -path './dist/*' 2>/dev/null || true)
if [ -n "$JS_FILES" ]; then
    # Look for process.env.something, but ignore common config folders
    raw_js_env=$(echo "$JS_FILES" | grep -v "config" | xargs grep -rn "process\.env\.[A-Za-z0-9_]" 2>/dev/null || true)
    if [ -n "$raw_js_env" ]; then
        echo "  [WARNING] Raw 'process.env' access found outside configuration modules:"
        echo "$raw_js_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

GO_FILES=$(find . -name "*.go" -not -path './.agents/*' 2>/dev/null || true)
if [ -n "$GO_FILES" ]; then
    raw_go_env=$(echo "$GO_FILES" | grep -v "config" | xargs grep -rn "os\.Getenv" 2>/dev/null || true)
    if [ -n "$raw_go_env" ]; then
        echo "  [WARNING] Raw 'os.Getenv' access found outside configuration modules:"
        echo "$raw_go_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

if [ "$RAW_ENV_FOUND" -eq 0 ]; then
    echo "  [PASS] Domain isolation looks healthy (no scattered raw env reads)."
fi

# 5. Check Git Upstream Synchronization
echo "Check 5: Git Upstream Synchronization Check"
# Attempt to fetch upstream changes silently to check sync state (gracefully handle failures/offline)
if command -v timeout >/dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" timeout 5 git fetch origin >/dev/null 2>&1 || true
elif command -v gtimeout >/dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" gtimeout 5 git fetch origin >/dev/null 2>&1 || true
else
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" git -c transfer.timeout=5 fetch origin >/dev/null 2>&1 || true
fi

LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "none")
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "none")
BASE=$(git merge-base HEAD @{u} 2>/dev/null || echo "none")

if [ "$LOCAL" = "none" ] || [ "$REMOTE" = "none" ]; then
    echo "  [WARNING] No upstream tracking branch set or Git repository not initialized."
elif [ "$LOCAL" = "$REMOTE" ]; then
    echo "  [PASS] Local branch is up-to-date with upstream."
elif [ "$LOCAL" = "$BASE" ]; then
    echo "  [FAIL] Workspace is behind upstream! Run 'git pull' before letting the agent modify files."
    FAILED=1
elif [ "$REMOTE" = "$BASE" ]; then
    echo "  [PASS] Local branch is ahead of upstream (unpushed commits)."
else
    echo "  [FAIL] Workspace has diverged from upstream! Please reconcile branches before modifying files."
    FAILED=1
fi

# 6. Check Schema Index Registration Compliance
echo "Check 6: Schema Index Registration Compliance"
SCHEMA_ERRORS=0
if [ -f ".agents/schema.md" ]; then
    if [ -d ".agents/schemas" ]; then
        for schema_file in .agents/schemas/*.md; do
            if [ -f "$schema_file" ]; then
                base_name=$(basename "$schema_file")
                # Verify registration in schema.md
                if ! grep -q "$base_name" ".agents/schema.md"; then
                    echo "  [FAIL] Domain schema file '$base_name' is NOT registered in '.agents/schema.md'!"
                    SCHEMA_ERRORS=$((SCHEMA_ERRORS + 1))
                fi
            fi
        done
    fi
else
    echo "  [FAIL] Primary schema index '.agents/schema.md' is missing!"
    SCHEMA_ERRORS=$((SCHEMA_ERRORS + 1))
fi

if [ "$SCHEMA_ERRORS" -eq 0 ]; then
    echo "  [PASS] All domain schemas are correctly indexed."
else
    FAILED=1
fi

# 7. Check Gitignore Configuration Compliance
echo "Check 7: Gitignore Configuration Compliance"
GITIGNORE_ERRORS=0
if [ -f ".gitignore" ]; then
    # Verify that .gitignore does NOT ignore .agents/ or AGENTS.md globally
    if grep -E -q "^\.agents/?$" .gitignore; then
        echo "  [FAIL] .gitignore ignores '.agents/' folder globally! Please remove it."
        GITIGNORE_ERRORS=$((GITIGNORE_ERRORS + 1))
    fi
    if grep -q "^AGENTS.md$" .gitignore; then
        echo "  [FAIL] .gitignore ignores 'AGENTS.md'! Please remove it."
        GITIGNORE_ERRORS=$((GITIGNORE_ERRORS + 1))
    fi
    # Verify that .agents/locks/ is ignored
    if ! grep -E -q "^\.agents/locks/?" .gitignore; then
        echo "  [WARNING] .gitignore does not ignore transient locks ('.agents/locks/')."
    fi
else
    echo "  [WARNING] No .gitignore file found in project root."
fi

if [ "$GITIGNORE_ERRORS" -eq 0 ]; then
    echo "  [PASS] Gitignore is correctly configured."
else
    FAILED=1
fi

# 8. Check Memory State Flag Enforcement
echo "Check 8: Memory State Flag Enforcement"
STATE_ERRORS=0
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    if [ -f "$MEMORY_FILE" ]; then
        if grep -Fq -- "- **State Flag**:" "$MEMORY_FILE"; then
            if ! grep -Ei -- "- \*\*State Flag\*\*:\s*\`?COMPLETED\`?" "$MEMORY_FILE" >/dev/null; then
                echo "  [FAIL] Commit rejected on branch '$CURRENT_BRANCH' because State Flag is not 'COMPLETED'!"
                echo "         Please complete your tasks and update memory.md State Flag to 'COMPLETED' first."
                STATE_ERRORS=$((STATE_ERRORS + 1))
            fi
        fi
    fi
else
    echo "  [PASS] Memory state flag checks bypassed on local feature branch '$CURRENT_BRANCH'."
fi

if [ "$STATE_ERRORS" -eq 0 ]; then
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        echo "  [PASS] Memory state flag is 'COMPLETED' for production commit."
    fi
else
    FAILED=1
fi

# 9. Check Token Budget Guard
echo "Check 9: Token Budget Guard"
BUDGET_FILE=".agents/token_budget.json"
if [ -f "$BUDGET_FILE" ] && command -v jq >/dev/null 2>&1; then
    MAX_BUDGET=$(jq -r '.max_token_budget' "$BUDGET_FILE")
    CURRENT_USAGE=$(jq -r '.current_token_usage' "$BUDGET_FILE")
    THRESHOLD=$(jq -r '.alert_threshold_percent' "$BUDGET_FILE")
    
    if [ "$MAX_BUDGET" -gt 0 ]; then
        PERCENT=$(( CURRENT_USAGE * 100 / MAX_BUDGET ))
        echo "  Current token usage: $CURRENT_USAGE / $MAX_BUDGET ($PERCENT%)"
        if [ "$CURRENT_USAGE" -ge "$MAX_BUDGET" ]; then
            echo "  [FAIL] Token budget exceeded! Current: $CURRENT_USAGE, Limit: $MAX_BUDGET."
            echo "         Please save your task checkpoint in workflows/ and handover the task."
            FAILED=1
        elif [ "$PERCENT" -ge "$THRESHOLD" ]; then
            echo "  [WARNING] Token usage is at $PERCENT% of budget. Consider saving and handing over."
        else
            echo "  [PASS] Token usage is within safe budget limits."
        fi
    fi
else
    echo "  [PASS] No active token budget file or jq tool found. Bypassing check."
fi

echo "=========================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "Workspace Status: VALIDATED"
    exit 0
else
    echo "Workspace Status: DEGRADED (Check issues detailed above)"
    exit 1
fi
