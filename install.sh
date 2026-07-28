# Antigravity Agent Core (AAC) One-Line Installer Script
# Usage: curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash

set -e

echo "🚀 Installing Antigravity Agent Core (AAC) v4.3.0..."


# Create target directory structure if needed
mkdir -p .agents/brain/schemas .agents/plans .agents/incidents .agents/scratch .agents/skills .agents/common .agents/locks

# Temporary clone directory
TMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/rafaelghif/antigravity-agents.git "$TMP_DIR" > /dev/null 2>&1


# Copy Core Directive and Configurations
cp "$TMP_DIR/AGENTS.md" ./AGENTS.md
cp -r "$TMP_DIR/.agents/"* ./.agents/

# Copy default .env.example if missing
if [ ! -f .env.example ]; then
  cp "$TMP_DIR/.env.example" ./.env.example
fi

# Clean up temporary directory
rm -rf "$TMP_DIR"

echo "✅ AAC v4.3.0 successfully installed into $(pwd)!"
echo "💡 Start your Antigravity CLI session (agy) to experience Task-Driven Zero-Amnesia autonomous coding."

