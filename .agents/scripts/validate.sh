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

echo "=========================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "Workspace Status: VALIDATED"
    exit 0
else
    echo "Workspace Status: DEGRADED (Check issues detailed above)"
    exit 1
fi
