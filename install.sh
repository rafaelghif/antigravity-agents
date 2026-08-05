#!/usr/bin/env bash
# Antigravity Agent Core (AAC) reproducible installer.
# Usage: curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash

set -Eeuo pipefail

readonly AAC_REF="v4.3.4"
readonly REPOSITORY="https://github.com/rafaelghif/antigravity-agents.git"
readonly TARGET_DIR="${AAC_TARGET_DIR:-$PWD}"
readonly TMP_DIR="$(mktemp -d)"
readonly BACKUP_DIR="$TARGET_DIR/.agents-backups/$(date -u +%Y%m%dT%H%M%SZ)"
trap 'rm -rf "$TMP_DIR"' EXIT

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'Required command not found: %s\n' "$1" >&2
    exit 1
  }
}

backup_if_present() {
  local source="$1"
  local destination="$BACKUP_DIR/$2"
  if [[ -e "$source" ]]; then
    mkdir -p "$(dirname "$destination")"
    cp -a "$source" "$destination"
  fi
}

require_command git
require_command cp
require_command mktemp

mkdir -p "$TARGET_DIR/.agents" "$TARGET_DIR/.agents/brain" "$TARGET_DIR/.agents/common" \
  "$TARGET_DIR/.agents/incidents" "$TARGET_DIR/.agents/locks" "$TARGET_DIR/.agents/plans" \
  "$TARGET_DIR/.agents/scratch" "$TARGET_DIR/.agents/skills" "$TARGET_DIR/scripts"

git clone --depth 1 --branch "$AAC_REF" "$REPOSITORY" "$TMP_DIR/source" >/dev/null

backup_if_present "$TARGET_DIR/AGENTS.md" AGENTS.md
backup_if_present "$TARGET_DIR/.agents/config.json" .agents/config.json
backup_if_present "$TARGET_DIR/.agents/TASK_TEMPLATE.md" .agents/TASK_TEMPLATE.md

cp "$TMP_DIR/source/AGENTS.md" "$TARGET_DIR/AGENTS.md"
if [[ ! -e "$TARGET_DIR/.env.example" ]]; then
  cp "$TMP_DIR/source/.env.example" "$TARGET_DIR/.env.example"
fi
cp "$TMP_DIR/source/.agents/config.json" "$TARGET_DIR/.agents/config.json"
cp "$TMP_DIR/source/.agents/TASK_TEMPLATE.md" "$TARGET_DIR/.agents/TASK_TEMPLATE.md"
cp "$TMP_DIR/source/.agents/antigravity-settings.example.json" "$TARGET_DIR/.agents/antigravity-settings.example.json"
cp "$TMP_DIR/source/.agents/mcp_config.json.example" "$TARGET_DIR/.agents/mcp_config.json.example"
cp -R "$TMP_DIR/source/.agents/brain/." "$TARGET_DIR/.agents/brain/"
cp -R "$TMP_DIR/source/.agents/common/." "$TARGET_DIR/.agents/common/"
cp -R "$TMP_DIR/source/.agents/skills/." "$TARGET_DIR/.agents/skills/"
cp "$TMP_DIR/source/scripts/validate.py" "$TARGET_DIR/scripts/validate.py"

python3 "$TARGET_DIR/scripts/validate.py"

printf 'AAC %s installed into %s\n' "$AAC_REF" "$TARGET_DIR"
printf 'Backups, when needed, are stored in %s\n' "$BACKUP_DIR"
printf 'Copy .agents/antigravity-settings.example.json into the global Antigravity CLI settings profile.\n'
