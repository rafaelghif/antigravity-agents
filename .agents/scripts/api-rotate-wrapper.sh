#!/usr/bin/env bash
# Antigravity API Auto-Rotation Command Wrapper
# Wraps execution of any agent CLI or command, automatically rotating API profiles 
# from '.agents/api_keys' if the command fails with a rate-limit error (exit code 429).
set -uo pipefail

# Find the helper script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SH="${SCRIPT_DIR}/helper.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 [command_to_run] [args...]" >&2
    echo "Example: $0 npx antigravity-cli task-run" >&2
    exit 1
fi

# Find available API profiles to count max retries
API_KEYS_FILE=""
if [ -f ".agents/api_keys" ]; then
    API_KEYS_FILE=".agents/api_keys"
elif [ -f "$HOME/.antigravity_api_keys" ]; then
    API_KEYS_FILE="$HOME/.antigravity_api_keys"
fi

MAX_RETRIES=1
if [ -n "$API_KEYS_FILE" ] && [ -f "$API_KEYS_FILE" ]; then
    num_profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=" "$API_KEYS_FILE" | cut -d'.' -f1 | sort -u | wc -l || echo "1")
    if [ "$num_profiles" -gt 0 ]; then
        MAX_RETRIES=$num_profiles
    fi
fi

retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    # Ensure active API keys are loaded
    if [ -f ".agents/active_api_keys" ]; then
        source ".agents/active_api_keys"
    else
        # If no profile is active, initialize the first available profile
        echo "No active API profile set. Initializing first available profile..."
        "$HELPER_SH" api-profile rotate >/dev/null 2>&1 || true
        if [ -f ".agents/active_api_keys" ]; then
            source ".agents/active_api_keys"
        fi
    fi

    # Run the wrapped command
    echo "[API-WRAPPER] Running wrapped command..."
    # Disable exit on error temporarily so we can catch exit code
    set +e
    "$@"
    exit_code=$?
    set -e

    if [ $exit_code -eq 0 ]; then
        exit 0
    # Catch typical rate limit / exhaustion codes: 
    # - 429: Too Many Requests
    # - 129: Common custom agent rate-limit exit code
    # - 3: Resource exhausted (gRPC status code)
    elif [ $exit_code -eq 429 ] || [ $exit_code -eq 129 ] || [ $exit_code -eq 173 ] || [ $exit_code -eq 3 ]; then
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            echo "[API-WRAPPER] Command exited with code $exit_code (Rate Limited/Quota Exhausted)."
            echo "[API-WRAPPER] Rotating API profile and retrying ($retry_count/$MAX_RETRIES)..."
            "$HELPER_SH" api-profile rotate --rate-limited
            sleep 1
        else
            echo "[API-WRAPPER] Command exited with code $exit_code. All available API profiles exhausted." >&2
            exit $exit_code
        fi
    else
        # Exit immediately on other execution failures
        exit $exit_code
    fi
done
