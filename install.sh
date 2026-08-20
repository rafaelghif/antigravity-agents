#!/usr/bin/env bash
# Antigravity Agent Core (AAC) reproducible installer.
# Usage: curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.40/install.sh | bash

set -Eeuo pipefail
umask 077

readonly AAC_REF="v4.4.40"
readonly REPOSITORY="https://github.com/rafaelghif/antigravity-agents.git"
readonly TARGET_DIR="${AAC_TARGET_DIR:-$PWD}"
readonly TMP_DIR="$(mktemp -d)"
readonly BACKUP_DIR="$TARGET_DIR/.agents-backups/$(date -u +%Y%m%dT%H%M%SZ)"
cleanup() {
  local exit_code=$?
  [[ $exit_code -ne 0 && -d "$BACKUP_DIR" ]] && cp -a -- "$BACKUP_DIR/." "$TARGET_DIR/" 2>/dev/null || true
  rm -rf "$TMP_DIR"
  exit $exit_code
}
trap cleanup EXIT

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
    mkdir -p -- "$(dirname "$destination")"
    cp -a -- "$source" "$destination"
  fi
}

copy_managed() {
  local source="$1"
  local destination="$TARGET_DIR/$2"
  backup_if_present "$destination" "$2"
  mkdir -p -- "$(dirname "$destination")"
  if [[ -d "$source" ]]; then
    mkdir -p -- "$destination"
    cp -a -- "$source/." "$destination/"
  else
    cp -a -- "$source" "$destination"
  fi
}

require_command git
require_command cp
require_command mktemp
require_command python3

mkdir -p -- "$TARGET_DIR/.agents" \
  "$TARGET_DIR/.agents/incidents" "$TARGET_DIR/.agents/locks" "$TARGET_DIR/.agents/plans" \
  "$TARGET_DIR/.agents/scratch" "$TARGET_DIR/scripts"


if [[ -f "$TARGET_DIR/.agents/config.json" ]]; then
  printf "=> Initiating AAC Upgrade to %s...\n" "$AAC_REF"
else
  printf "=> Initiating AAC Clean Install of %s...\n" "$AAC_REF"
fi

if [[ -f "$TARGET_DIR/.agents/brain/rules.md" ]]; then
  cp -- "$TARGET_DIR/.agents/brain/rules.md" "$TMP_DIR/rules.md.bak"
fi

git clone --depth 1 --branch "$AAC_REF" "$REPOSITORY" "$TMP_DIR/source" >/dev/null

python3 "$TMP_DIR/source/scripts/validate.py"

copy_managed "$TMP_DIR/source/AGENTS.md" AGENTS.md
copy_managed "$TMP_DIR/source/GEMINI.md" GEMINI.md
if [[ ! -e "$TARGET_DIR/.env.example" ]]; then
  cp -- "$TMP_DIR/source/.env.example" "$TARGET_DIR/.env.example"
fi
copy_managed "$TMP_DIR/source/.agents/config.json" .agents/config.json
copy_managed "$TMP_DIR/source/.agents/TASK_TEMPLATE.md" .agents/TASK_TEMPLATE.md
copy_managed "$TMP_DIR/source/.agents/antigravity-settings.example.json" .agents/antigravity-settings.example.json
copy_managed "$TMP_DIR/source/.agents/antigravity-compatibility.json" .agents/antigravity-compatibility.json
copy_managed "$TMP_DIR/source/.agents/mcp_config.json.example" .agents/mcp_config.json.example
copy_managed "$TMP_DIR/source/.agents/brain" .agents/brain

if [[ -f "$TMP_DIR/rules.md.bak" ]]; then
  cp -- "$TMP_DIR/rules.md.bak" "$TARGET_DIR/.agents/brain/rules.md"
fi

copy_managed "$TMP_DIR/source/.agents/common" .agents/common
copy_managed "$TMP_DIR/source/.agents/agents" .agents/agents
copy_managed "$TMP_DIR/source/.agents/skills" .agents/skills
copy_managed "$TMP_DIR/source/scripts/validate.py" scripts/validate.py
copy_managed "$TMP_DIR/source/scripts/verify.py" scripts/verify.py

printf 'AAC %s successfully configured in %s\n' "$AAC_REF" "$TARGET_DIR"
printf 'Backups, when needed, are stored in %s\n' "$BACKUP_DIR"
printf 'Copy .agents/antigravity-settings.example.json into the global Antigravity CLI settings profile.\n'
