#!/usr/bin/env bash
# Antigravity Agent Core (AAC) reproducible installer & upgrader.
# Usage: curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash

set -Eeuo pipefail
umask 077

readonly REPOSITORY="https://github.com/rafaelghif/antigravity-agents.git"

if [[ -z "${AAC_REF:-}" ]]; then
  AAC_REF="$(git ls-remote --tags --refs "$REPOSITORY" 2>/dev/null | cut -d/ -f3 | sort -V | tail -n 1 || echo "")"
  AAC_REF="${AAC_REF:-v4.29.0}"
fi
# Version marker for validation:  AAC_REF="v4.29.0"
readonly AAC_REF
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

for brain_file in rules.md memory.md ANCHOR.md active_context.md soul.md schema.md; do
  if [[ -f "$TARGET_DIR/.agents/brain/$brain_file" ]]; then
    cp -- "$TARGET_DIR/.agents/brain/$brain_file" "$TMP_DIR/${brain_file}.bak"
  fi
done

git clone --depth 1 --branch "$AAC_REF" "$REPOSITORY" "$TMP_DIR/source" >/dev/null

python3 "$TMP_DIR/source/scripts/validate.py"

copy_managed "$TMP_DIR/source/AGENTS.md" AGENTS.md
copy_managed "$TMP_DIR/source/GEMINI.md" GEMINI.md
if [[ ! -e "$TARGET_DIR/.env.example" && -f "$TMP_DIR/source/.env.example" ]]; then
  cp -- "$TMP_DIR/source/.env.example" "$TARGET_DIR/.env.example"
fi
copy_managed "$TMP_DIR/source/.agents" .agents
copy_managed "$TMP_DIR/source/scripts" scripts

# Exclude internal AAC workflows and ensure upstream GitHub Actions workflows do not pollute target project
rm -rf -- "$TARGET_DIR/.agents/workflows"
rm -f -- "$TARGET_DIR/.github/workflows/agent-gates.yml" "$TARGET_DIR/.github/workflows/agentic-cicd.yml"
rmdir "$TARGET_DIR/.github/workflows" 2>/dev/null || true
rmdir "$TARGET_DIR/.github" 2>/dev/null || true

for brain_file in rules.md memory.md ANCHOR.md active_context.md soul.md schema.md; do
  if [[ -f "$TMP_DIR/${brain_file}.bak" ]]; then
    cp -- "$TMP_DIR/${brain_file}.bak" "$TARGET_DIR/.agents/brain/$brain_file"
  fi
done

printf 'AAC %s successfully configured in %s\n' "$AAC_REF" "$TARGET_DIR"
printf 'Backups, when needed, are stored in %s\n' "$BACKUP_DIR"
printf 'Copy .agents/antigravity-settings.example.json into the global Antigravity CLI settings profile.\n'
