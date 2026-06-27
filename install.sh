#!/usr/bin/env bash
# POSIX-compliant installer for Antigravity Agent Core (AAC) V2
set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_ABS=$(realpath "$TARGET_DIR")

echo "=========================================================="
echo "   Installing Antigravity Agent Core V2..."
echo "   Target Directory: $TARGET_ABS"
echo "=========================================================="

# 1. Verify target directory and backup existing installation for upgrade
mkdir -p "$TARGET_ABS"

TIMESTAMP=""
if [ -d "$TARGET_ABS/.agents" ]; then
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  echo "Existing installation found! Archiving to .agents_backup_$TIMESTAMP..."
  mv "$TARGET_ABS/.agents" "$TARGET_ABS/.agents_backup_$TIMESTAMP"
  
  if [ -f "$TARGET_ABS/AGENTS.md" ]; then
    echo "Backing up AGENTS.md to AGENTS.md.backup_$TIMESTAMP..."
    cp "$TARGET_ABS/AGENTS.md" "$TARGET_ABS/AGENTS.md.backup_$TIMESTAMP"
  fi
fi

# Get source path
SRC_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# 2. Safely acquire and copy agent directory structure
mkdir -p "$TARGET_ABS/.agents"

if [ -d "$SRC_DIR/.agents" ]; then
  echo "Using local source files from: $SRC_DIR"
  
  # Copy files recursively excluding __pycache__, locks.json, git_profiles.json, .DS_Store, *.pyc
  (
    cd "$SRC_DIR"
    find .agents -type f \
      ! -path "*/__pycache__/*" \
      ! -path "*/.git/*" \
      ! -name "git_profiles.json" \
      ! -name "locks.json" \
      ! -name ".DS_Store" \
      ! -name "*.pyc" \
      ! -name "*.pyo" \
      ! -path ".agents/memory/*" \
      -exec sh -c '
        for file; do
          dest_file="'"$TARGET_ABS"'/$file"
          mkdir -p "$(dirname "$dest_file")"
          cp -n "$file" "$dest_file" 2>/dev/null || true
        done
      ' _ {} +
  )
  
  # Initialize clean memory folder in target
  mkdir -p "$TARGET_ABS/.agents/memory/decisions"
  if [ -d "$SRC_DIR/.agents/memory/templates" ]; then
    for t in "$SRC_DIR/.agents/memory/templates/"*.template; do
      [ -f "$t" ] || continue
      filename_t=$(basename "$t" .template)
      cp -n "$t" "$TARGET_ABS/.agents/memory/$filename_t"
    done
  fi

  cp -n "$SRC_DIR/helper.sh" "$TARGET_ABS/helper.sh" || true
  cp -n "$SRC_DIR/helper.ps1" "$TARGET_ABS/helper.ps1" || true
  
  if [ ! -f "$TARGET_ABS/AGENTS.md" ]; then
    cp "$SRC_DIR/AGENTS.md" "$TARGET_ABS/AGENTS.md"
    echo "Created AGENTS.md."
  else
    echo "AGENTS.md already exists. Skipping overwrite."
  fi
  
  # Run local bootstrap.sh
  bash "$SRC_DIR/bootstrap.sh"
else
  echo "Local source files not found. Downloading Antigravity Agent Core from GitHub..."
  
  # Create a temporary directory
  TEMP_DIR=$(mktemp -d)
  ZIP_PATH="$TEMP_DIR/repo.zip"
  
  # Download ZIP
  REPO_URL="https://github.com/rafaelghif/antigravity-agents/archive/refs/heads/main.zip"
  if command -v curl &>/dev/null; then
    curl -L "$REPO_URL" -o "$ZIP_PATH"
  elif command -v wget &>/dev/null; then
    wget -O "$ZIP_PATH" "$REPO_URL"
  else
    echo "Error: Neither curl nor wget is installed. Cannot download source files." >&2
    rm -rf "$TEMP_DIR"
    exit 1
  fi
  
  # Extract ZIP
  if command -v unzip &>/dev/null; then
    unzip -q "$ZIP_PATH" -d "$TEMP_DIR"
  else
    # Fallback to python for unzipping if unzip is missing
    python3 -c "import zipfile; zipfile.ZipFile('$ZIP_PATH').extractall('$TEMP_DIR')"
  fi
  
  # Find extracted folder (usually antigravity-agents-main)
  EXTRACTED_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "antigravity-agents-*" | head -n 1)
  
  if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR/.agents" ]; then
    echo "Error: Extracted repository folder not found or invalid." >&2
    rm -rf "$TEMP_DIR"
    exit 1
  fi
  
  # Copy files recursively excluding __pycache__, locks.json, git_profiles.json, .DS_Store, *.pyc
  (
    cd "$EXTRACTED_DIR"
    find .agents -type f \
      ! -path "*/__pycache__/*" \
      ! -path "*/.git/*" \
      ! -name "git_profiles.json" \
      ! -name "locks.json" \
      ! -name ".DS_Store" \
      ! -name "*.pyc" \
      ! -name "*.pyo" \
      ! -path ".agents/memory/*" \
      -exec sh -c '
        for file; do
          dest_file="'"$TARGET_ABS"'/$file"
          mkdir -p "$(dirname "$dest_file")"
          cp -n "$file" "$dest_file" 2>/dev/null || true
        done
      ' _ {} +
  )
  
  # Initialize clean memory folder in target
  mkdir -p "$TARGET_ABS/.agents/memory/decisions"
  if [ -d "$EXTRACTED_DIR/.agents/memory/templates" ]; then
    for t in "$EXTRACTED_DIR/.agents/memory/templates/"*.template; do
      [ -f "$t" ] || continue
      filename_t=$(basename "$t" .template)
      cp -n "$t" "$TARGET_ABS/.agents/memory/$filename_t"
    done
  fi

  cp -n "$EXTRACTED_DIR/helper.sh" "$TARGET_ABS/helper.sh" || true
  cp -n "$EXTRACTED_DIR/helper.ps1" "$TARGET_ABS/helper.ps1" || true
  
  if [ ! -f "$TARGET_ABS/AGENTS.md" ]; then
    cp "$EXTRACTED_DIR/AGENTS.md" "$TARGET_ABS/AGENTS.md"
    echo "Created AGENTS.md."
  else
    echo "AGENTS.md already exists. Skipping overwrite."
  fi
  
  # Run bootstrap.sh from extracted folder inside target folder context
  (cd "$TARGET_ABS" && bash "$EXTRACTED_DIR/bootstrap.sh")
  
  # Cleanup
  rm -rf "$TEMP_DIR"
fi

chmod +x "$TARGET_ABS/helper.sh"

# 3. Initialize Git if not present in target
if [ ! -d "$TARGET_ABS/.git" ]; then
  echo "Initializing empty Git repository in target directory..."
  git -C "$TARGET_ABS" init
fi

# 4. Execute final synchronization in target directory
cd "$TARGET_ABS"
./helper.sh sync

if [ -n "${TIMESTAMP:-}" ]; then
  echo ""
  echo "=========================================================="
  echo "   [WARNING] Upgrade Backup Triggered!                    "
  echo "=========================================================="
  echo "Your old .agents config has been archived to:"
  echo "  .agents_backup_$TIMESTAMP"
  echo "Your old AGENTS.md has been backed up to:"
  echo "  AGENTS.md.backup_$TIMESTAMP"
  echo "To restore custom tasks, issues, or profiles, copy them"
  echo "from the backup folder to the active .agents directory."
  echo "=========================================================="
fi

echo "=========================================================="
echo "   AAC V2 Installation Completed Successfully!            "
echo "   Run './helper.sh validate' in the target folder to test."
echo "=========================================================="
