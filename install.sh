#!/usr/bin/env bash

# Antigravity Agent Core (AAC) One-Line Installer Script
# Usage: curl -fsSL https://raw.githubusercontent.com/rafaelghifari/antigravity-agents/main/install.sh | bash

set -e

echo "🚀 Installing Antigravity Agent Core (AAC) v4.2.0..."

# Create target directory structure if needed
mkdir -p .agents/brain/schemas .agents/plans .agents/incidents .agents/scratch .agents/skills .agents/common

# Temporary clone directory
TMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/rafaelghifari/antigravity-agents.git "$TMP_DIR" > /dev/null 2>&1

# Copy Core Directive and Configurations
cp "$TMP_DIR/AGENTS.md" ./AGENTS.md
cp -r "$TMP_DIR/.agents/"* ./.agents/

# Copy default .env.example if missing
if [ ! -f .env.example ]; then
  cp "$TMP_DIR/.env.example" ./.env.example
fi

# Reset clean state.json for new user onboarding (Zero state leakage)
if [ -f .agents/brain/state.json ]; then
  cat << 'EOF' > .agents/brain/state.json
{
  "session_id": null,
  "current_branch": "main",
  "active_task": null,
  "current_tier": "Tier 1",
  "current_step": "idle",
  "token_usage": {
    "current_used": 0,
    "max_budget": 100000,
    "last_compaction_timestamp": null
  },
  "active_subagents": [],
  "claimed_tasks": {},
  "last_updated": "2026-07-27T00:00:00Z"
}
EOF
fi


# Clean up temporary directory
rm -rf "$TMP_DIR"

echo "✅ AAC v4.2.0 successfully installed into $(pwd)!"
echo "💡 Start your Antigravity CLI session (agy) to experience Zero-Amnesia, Zero-Yes-Man autonomous coding."
