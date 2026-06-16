#!/usr/bin/env bash
# Antigravity Agent Core - Workspace & Security Validator
# Validates workspace rules, scans for credentials, checks memory size, and details active locks.

set -euo pipefail

# Color Definitions (TTY-aware)
if [ -t 1 ]; then
    RED='\033[91m'
    GREEN='\033[92m'
    YELLOW='\033[93m'
    BLUE='\033[94m'
    CYAN='\033[96m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Override echo to support colors dynamically
echo() {
    local msg="$*"
    if [ -t 1 ]; then
        msg="${msg//\[PASS\]/[${GREEN}${BOLD}PASS${NC}]}"
        msg="${msg//\[WARNING\]/[${YELLOW}${BOLD}WARNING${NC}]}"
        msg="${msg//\[FAIL\]/[${RED}${BOLD}FAIL${NC}]}"
        if [[ "$msg" =~ ^Check\ [0-9]+: ]]; then
            msg="${msg/Check /${CYAN}${BOLD}Check }"
            msg="${msg/: /:${NC} }"
        fi
        if [[ "$msg" == "Starting Antigravity Agent Workspace Validation..." ]]; then
            msg="${CYAN}${BOLD}${msg}${NC}"
        fi
        if [[ "$msg" == "Workspace Status:"* ]]; then
            if [[ "$msg" == *"VALIDATED"* ]]; then
                msg="${msg/VALIDATED/${GREEN}${BOLD}VALIDATED${NC}}"
            else
                msg="${msg/DEGRADED/${RED}${BOLD}DEGRADED${NC}}"
            fi
        fi
    fi
    command echo -e "$msg"
}

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
PROJECT_RULES=".agents/rules/project_rules.md"

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
    -not -path './venv/*' \
    -not -path './env/*' \
    -not -path './target/*' \
    -not -path './vendor/*' \
    -not -path './out/*' \
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
JS_FILES=$(find . \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) -not -path './.agents/*' -not -path './node_modules/*' -not -path './dist/*' -not -path './venv/*' -not -path './env/*' -not -path './target/*' -not -path './vendor/*' -not -path './out/*' 2>/dev/null || true)
if [ -n "$JS_FILES" ]; then
    # Look for process.env.something, but ignore common config and test folders
    raw_js_env=$(echo "$JS_FILES" | grep -v "config" | grep -v "test" | xargs grep -rn "process\.env\.[A-Za-z0-9_]" 2>/dev/null || true)
    if [ -n "$raw_js_env" ]; then
        echo "  [WARNING] Raw 'process.env' access found outside configuration modules:"
        echo "$raw_js_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

GO_FILES=$(find . -name "*.go" -not -path './.agents/*' -not -path './vendor/*' -not -path './venv/*' -not -path './env/*' 2>/dev/null || true)
if [ -n "$GO_FILES" ]; then
    raw_go_env=$(echo "$GO_FILES" | grep -v "config" | grep -v "test" | xargs grep -rn "os\.Getenv" 2>/dev/null || true)
    if [ -n "$raw_go_env" ]; then
        echo "  [WARNING] Raw 'os.Getenv' access found outside configuration modules:"
        echo "$raw_go_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

PY_FILES=$(find . -name "*.py" -not -path './.agents/*' -not -path './venv/*' -not -path './env/*' 2>/dev/null || true)
if [ -n "$PY_FILES" ]; then
    raw_py_env=$(echo "$PY_FILES" | grep -v "config" | grep -v "test" | xargs grep -rnE "os\.(environ|getenv|environ\.get)\b" 2>/dev/null || true)
    if [ -n "$raw_py_env" ]; then
        echo "  [WARNING] Raw 'os.environ/os.getenv' access found outside configuration modules:"
        echo "$raw_py_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

if [ "$RAW_ENV_FOUND" -eq 0 ]; then
    echo "  [PASS] Domain isolation looks healthy (no scattered raw env reads)."
fi

# 5. Check Git Upstream Synchronization
echo "Check 5: Git Upstream Synchronization Check"
# Attempt to fetch upstream changes silently to check sync state (gracefully handle failures/offline)
# Use a pure Bash background process watchdog to enforce a strict 5-second timeout and prevent hanging.
if git remote | grep -q "^origin$"; then
    (
        GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" git -c transfer.timeout=5 fetch origin >/dev/null 2>&1 &
        cmd_pid=$!
        (
            sleep 5
            kill -0 "$cmd_pid" 2>/dev/null && kill -9 "$cmd_pid" 2>/dev/null || true
        ) &
        watchdog_pid=$!
        wait "$cmd_pid" 2>/dev/null || true
        kill -9 "$watchdog_pid" 2>/dev/null || true
    ) || true
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

# 7. Check Gitignore & Antigravityignore Configuration Compliance
echo "Check 7: Gitignore & Antigravityignore Compliance"
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

    # Auto-heal transient files ignore in .gitignore
    HEALED_GI=0
    for pattern in ".agents/locks/" ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name" ".agents/cooldowns.json"; do
        if ! grep -q "^$pattern" .gitignore; then
            echo "  [WARNING] .gitignore does not ignore transient: '$pattern'. Auto-healing..."
            echo "$pattern" >> .gitignore
            HEALED_GI=1
        fi
    done
    if [ $HEALED_GI -eq 1 ]; then
        echo "  [PASS] .gitignore auto-healed successfully."
    fi
else
    echo "  [WARNING] No .gitignore file found in project root."
fi

if [ -f ".antigravityignore" ]; then
    # Auto-heal transient files ignore in .antigravityignore
    HEALED_AG=0
    for pattern in ".agents/locks/" ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name" ".agents/cooldowns.json"; do
        if ! grep -q "^$pattern" .antigravityignore; then
            echo "  [WARNING] .antigravityignore does not ignore transient: '$pattern'. Auto-healing..."
            echo "$pattern" >> .antigravityignore
            HEALED_AG=1
        fi
    done
    if [ $HEALED_AG -eq 1 ]; then
        echo "  [PASS] .antigravityignore auto-healed successfully."
    fi
fi

if [ "$GITIGNORE_ERRORS" -eq 0 ]; then
    echo "  [PASS] Gitignore & Antigravityignore configurations are validated."
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
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import sys; sys.path.insert(0, '.agents/scripts/cli'); import utils; utils.load_budget()" || true
fi
if [ -f "$BUDGET_FILE" ] && command -v jq >/dev/null 2>&1; then
    # Auto-detect profile from active_api_profile_name
    PROFILE=""
    if [ -f ".agents/active_api_profile_name" ]; then
        PROFILE=$(cat ".agents/active_api_profile_name" | xargs)
    fi

    # Check if profile exists in profiles
    HAS_PROFILE=0
    if [ -n "$PROFILE" ]; then
        if jq -e --arg prof "$PROFILE" '.profiles[$prof] != null' "$BUDGET_FILE" >/dev/null 2>&1; then
            HAS_PROFILE=1
        fi
    fi

    MAX_BUDGET=0
    CURRENT_USAGE=0
    THRESHOLD=$(jq -r '.alert_threshold_percent // 90' "$BUDGET_FILE")

    if [ $HAS_PROFILE -eq 1 ]; then
        MAX_BUDGET=$(jq -r --arg prof "$PROFILE" '.profiles[$prof].max_token_budget // 0' "$BUDGET_FILE")
        CURRENT_USAGE=$(jq -r --arg prof "$PROFILE" '.profiles[$prof].current_token_usage // 0' "$BUDGET_FILE")
        echo "  Checking budget for active API profile: '$PROFILE'"
    else
        MAX_BUDGET=$(jq -r '.max_token_budget // 0' "$BUDGET_FILE")
        CURRENT_USAGE=$(jq -r '.current_token_usage // 0' "$BUDGET_FILE")
        echo "  Checking global token budget"
    fi
    
    if [ "$MAX_BUDGET" -gt 0 ]; then
        PERCENT=$(( CURRENT_USAGE * 100 / MAX_BUDGET ))
        echo "  Current token usage: $CURRENT_USAGE / $MAX_BUDGET ($PERCENT%)"
        if [ "$CURRENT_USAGE" -ge "$MAX_BUDGET" ]; then
            echo "  [FAIL] Token budget exceeded! Current: $CURRENT_USAGE, Limit: $MAX_BUDGET."
            echo "         Please save your task checkpoint in workflows/ and handover the task."
            FAILED=1
        elif [ "$PERCENT" -ge 95 ]; then
            echo "  [FAIL] Token usage has reached critical threshold ($PERCENT% >= 95%)! All operations blocked."
            echo "         Please request a budget increase or manually reset the usage log."
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

# 10. Check ADR Compliance Check
echo "Check 10: ADR Compliance Check"
ADR_ERRORS=0
if [ -f ".agents/adr.md" ]; then
    if [ -d ".agents/adrs" ]; then
        max_num=0
        for adr_file in .agents/adrs/*.md; do
            if [ -f "$adr_file" ]; then
                base_name=$(basename "$adr_file")
                # Verify registration in adr.md
                if ! grep -q "$base_name" ".agents/adr.md"; then
                    echo "  [FAIL] Architectural Decision Record file '$base_name' is NOT registered in '.agents/adr.md'!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                # Check for placeholders and template defaults
                if grep -i -q -E "TODO|FIXME|\[placeholder\]|Describe the problem|Describe the decision|Describe the result" "$adr_file"; then
                    echo "  [FAIL] ADR file '$base_name' contains placeholder text (TODO/FIXME/placeholder/template default)!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                # Check for required sections
                if ! grep -q "## Context" "$adr_file" || ! grep -q "## Decision" "$adr_file" || ! grep -q "## Consequences" "$adr_file"; then
                    echo "  [FAIL] ADR file '$base_name' is missing required sections (Context, Decision, Consequences)!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                
                # Extract sequence number to check for gaps later
                if [[ "$base_name" =~ ^([0-9]{3})- ]]; then
                    num=$((10#${BASH_REMATCH[1]}))
                    if [ "$num" -gt "$max_num" ]; then
                        max_num=$num
                    fi
                fi
            fi
        done
        
        # Gaps check
        if [ "$max_num" -gt 0 ]; then
            for ((i=1; i<=max_num; i++)); do
                padded_num=$(printf "%03d" $i)
                found=0
                for f in .agents/adrs/${padded_num}-*.md; do
                    if [ -e "$f" ]; then
                        found=1
                        break
                    fi
                done
                if [ "$found" -eq 0 ]; then
                    echo "  [FAIL] Missing ADR in sequence: ADR-${padded_num} is not found!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
            done
        fi
        
        # Bidirectional sync: check if registered files in adr.md actually exist
        links=$(grep -o -E "file://\./adrs/[^)]+\.md" ".agents/adr.md" | sed 's|file://./||' || true)
        for link in $links; do
            if [ ! -f ".agents/$link" ]; then
                echo "  [FAIL] ADR index references non-existent file '.agents/$link'!"
                ADR_ERRORS=$((ADR_ERRORS + 1))
            fi
        done
    fi
else
    echo "  [FAIL] Primary ADR index '.agents/adr.md' is missing!"
    ADR_ERRORS=$((ADR_ERRORS + 1))
fi

if [ "$ADR_ERRORS" -eq 0 ]; then
    echo "  [PASS] All Architectural Decision Records are correctly indexed and complete."
else
    FAILED=1
fi

# 11. Check Git Configuration & Profile Compliance
echo "Check 11: Git Configuration & Profile Compliance"
GIT_ERRORS=0
PROFILES_FILE=".agents/git_profiles"
if [ -f "$PROFILES_FILE" ]; then
    # Verify profiles syntax and check for missing names/emails
    while IFS= read -r line || [ -n "$line" ]; do
        # Ignore comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        
        # Check if the line is a valid key-value pair
        if [[ "$line" =~ ^([a-zA-Z0-9_\-]+)\.(name|email|ssh_key)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            prop="${BASH_REMATCH[2]}"
            val="${BASH_REMATCH[3]}"
            
            # Check for dummy/placeholder emails in defined profiles
            if [ "$prop" = "email" ]; then
                if [[ "$val" =~ ^(work@company\.com|personal@gmail\.com|side@project\.com)$ ]]; then
                    echo "  [WARNING] Profile '$key' uses a default template email: '$val'."
                fi
            fi
            
            # Verify if SSH key file path exists if specified
            if [ "$prop" = "ssh_key" ] && [ -n "$val" ]; then
                resolved_key="$val"
                if [[ "$resolved_key" == \~/* ]]; then
                    resolved_key="${resolved_key/\~/$HOME}"
                fi
                if [ ! -f "$resolved_key" ]; then
                    echo "  [WARNING] Profile '$key' specifies an SSH key file that does not exist: '$val'."
                fi
            fi
        fi
    done < "$PROFILES_FILE"
fi

local_name=$(git config --local user.name 2>/dev/null || echo "")
local_email=$(git config --local user.email 2>/dev/null || echo "")
if [ -n "$local_name" ] && [ -n "$local_email" ]; then
    # Warn if local config is a generic template
    if [[ "$local_email" =~ ^(work@company\.com|personal@gmail\.com|side@project\.com)$ ]]; then
        echo "  [WARNING] Local Git config user.email uses a placeholder email: '$local_email'."
    fi
fi

if [ "$GIT_ERRORS" -eq 0 ]; then
    echo "  [PASS] Git configurations and profiles are validated."
else
    FAILED=1
fi

# 12. Check API Configuration & Profile Compliance
echo "Check 12: API Configuration & Profile Compliance"
API_ERRORS=0
API_KEYS_FILE=".agents/api_keys"
if [ -f "$API_KEYS_FILE" ]; then
    # Verify profiles syntax and check for placeholder values
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        
        if [[ "$line" =~ ^([a-zA-Z0-9_\-]+)\.([A-Z0-9_]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            prop="${BASH_REMATCH[2]}"
            val="${BASH_REMATCH[3]}"
            
            if [[ "$val" =~ _key_here$ ]] || [ "$val" = "your_api_key_here" ]; then
                echo "  [WARNING] API Profile '$key' uses a placeholder value for '$prop': '$val'."
            fi
        else
            echo "  [FAIL] Invalid syntax in $API_KEYS_FILE: '$line'. Must be in format: profile.VARIABLE_NAME=value"
            API_ERRORS=$((API_ERRORS + 1))
        fi
    done < "$API_KEYS_FILE"
fi

# Ensure secrets and active state files are in .gitignore
if [ -f ".gitignore" ]; then
    for ignore_pattern in ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name"; do
        if ! grep -q "^$ignore_pattern" .gitignore; then
            echo "  [FAIL] .gitignore compliance: '$ignore_pattern' is not ignored. Please add it to your .gitignore to protect credentials."
            API_ERRORS=$((API_ERRORS + 1))
        fi
    done
fi

if [ "$API_ERRORS" -eq 0 ]; then
    echo "  [PASS] API configurations and profiles are validated and secure."
else
    FAILED=1
fi

# 13. Check CHANGELOG.md Format (Keep a Changelog Compliance)
echo "Check 13: Keep a Changelog Compliance"
CHANGELOG_ERRORS=0
if [ -f "CHANGELOG.md" ]; then
    if ! head -n 1 CHANGELOG.md | grep -q "^# Changelog" ; then
        echo "  [FAIL] CHANGELOG.md must start with '# Changelog' header."
        CHANGELOG_ERRORS=$((CHANGELOG_ERRORS + 1))
    fi
    INVALID_HEADERS=$(grep "^## " CHANGELOG.md | grep -Ev "^## \[(Unreleased|[0-9]+\.[0-9]+\.[0-9]+)\]( - [0-9]{4}-[0-9]{2}-[0-9]{2})?" || true)
    if [ -n "$INVALID_HEADERS" ]; then
        echo "  [FAIL] CHANGELOG.md contains invalid version headers:"
        echo "$INVALID_HEADERS" | sed 's/^/         /'
        CHANGELOG_ERRORS=$((CHANGELOG_ERRORS + 1))
    fi
else
    echo "  [WARNING] No CHANGELOG.md file found in project root."
fi

if [ "$CHANGELOG_ERRORS" -eq 0 ]; then
    echo "  [PASS] CHANGELOG.md matches Keep a Changelog compliance."
else
    FAILED=1
fi

# 14. Check for TODO/FIXME Annotations in Staged Code
echo "Check 14: Staged Code Quality (TODO/FIXME Guard)"
TODO_ERRORS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Get staged files excluding .md files, bootstrap.sh, and files inside .agents/
    STAGED_CODE_FILES=$(git diff --cached --name-only | grep -Ev "\.md$" | grep -v "^bootstrap\.sh$" | grep -Ev "^\.agents/" || true)
    for file in $STAGED_CODE_FILES; do
        TODO_LINES=$(git diff --cached -- "$file" | grep "^+[^+]" | grep -Ei "\b(TODO|FIXME)\b" || true)
        if [ -n "$TODO_LINES" ]; then
            echo "  [FAIL] Quality Guard: Staged file '$file' contains TODO or FIXME annotations:"
            echo "$TODO_LINES" | sed 's/^/         /'
            TODO_ERRORS=$((TODO_ERRORS + 1))
        fi
    done
fi

if [ "$TODO_ERRORS" -eq 0 ]; then
    echo "  [PASS] Staged changes contain no TODO or FIXME annotations."
else
    FAILED=1
fi

# 15. Check for Staged Transient Files & Config Leak Guard
echo "Check 15: Staged Transient Files & Leak Guard"
LEAK_ERRORS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    STAGED_FILES=$(git diff --cached --name-only)
    for file in $STAGED_FILES; do
        if [[ "$file" =~ \.lock$ ]] || [[ "$file" =~ active_api_keys ]] || [[ "$file" =~ cooldowns\.json$ ]]; then
            echo "  [FAIL] Leak Guard: Transient file '$file' is staged for commit! Please unstage it."
            LEAK_ERRORS=$((LEAK_ERRORS + 1))
        fi
    done
fi

if [ "$LEAK_ERRORS" -eq 0 ]; then
    echo "  [PASS] No transient files or credentials are staged."
else
    FAILED=1
fi

echo "=========================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "Workspace Status: VALIDATED"
    exit 0
else
    echo "Workspace Status: DEGRADED (Check issues detailed above)"
    exit 1
fi
