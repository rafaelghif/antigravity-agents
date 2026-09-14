#!/usr/bin/env bash
# AAC (Antigravity Agent Core) Installer for Linux / macOS
# Usage:
#   Local:  bash install.sh
#   Remote: curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.sh | bash

set -e

TARGET_DIR="$(pwd)"
echo -e "\n🚀 Installing AAC (Antigravity Agent Core v5.0.1)..."
echo -e "Target: ${TARGET_DIR}\n"

TEMP_ZIP="/tmp/aac-main.zip"
TEMP_DIR="/tmp/aac-temp"

cleanup() {
  rm -f "$TEMP_ZIP"
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

echo "📥 Downloading framework archive from GitHub..."
curl -fsSL "https://github.com/rafaelghif/antigravity-agents-core/archive/refs/heads/main.zip" -o "$TEMP_ZIP"

rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
unzip -q "$TEMP_ZIP" -d "$TEMP_DIR"

SOURCE_ROOT="$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"

# 1. Copy .agents directory
echo "📦 Copying .agents/ (rules, skills, hooks, plugins)..."
cp -r "${SOURCE_ROOT}/.agents" "${TARGET_DIR}/"

# 2. Copy root context and directives (NEVER copy package.json)
for file in AGENTS.md GEMINI.md CONTEXT.md; do
  if [ -f "${SOURCE_ROOT}/${file}" ]; then
    if [ ! -f "${TARGET_DIR}/${file}" ]; then
      cp "${SOURCE_ROOT}/${file}" "${TARGET_DIR}/${file}"
      echo "📄 Created ${file}"
    else
      echo "⏩ Skipped ${file} (already exists)"
    fi
  fi
done

# 3. Create .scratch directory
mkdir -p "${TARGET_DIR}/.scratch"
echo "# Ephemeral scratchpad directory" > "${TARGET_DIR}/.scratch/.gitkeep"
echo "📁 Created .scratch/ directory"

# 4. Update .gitignore
GITIGNORE="${TARGET_DIR}/.gitignore"
RULES="
# Antigravity Runtime & Ephemeral State
.gemini/
*.log
*.tmp
.scratch/*
!.scratch/.gitkeep
handoff.md

# Credentials & MCP Secrets
.agents/mcp_config.json
!.agents/mcp_config.example.json
.agents/plugins/**/mcp_config.json
!.agents/plugins/**/mcp_config.example.json"

if [ -f "$GITIGNORE" ]; then
  if ! grep -q "\.scratch/\*" "$GITIGNORE"; then
    echo "$RULES" >> "$GITIGNORE"
    echo "🛡️ Appended Antigravity guardrails to .gitignore"
  fi
else
  echo "$RULES" > "$GITIGNORE"
  echo "🛡️ Created .gitignore with Antigravity guardrails"
fi

echo -e "\n✅ Installation successful! (Zero package.json pollution)"
echo -e "👉 Open this repository in Antigravity IDE or Antigravity 2.0 to begin.\n"
