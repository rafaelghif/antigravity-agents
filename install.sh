#!/usr/bin/env bash
# POSIX-compliant installer for Antigravity Agent Core (AAC) V2
set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_ABS=$(realpath "$TARGET_DIR")

echo "=========================================================="
echo "   Installing Antigravity Agent Core V2..."
echo "   Target Directory: $TARGET_ABS"
echo "=========================================================="

# 1. Verify target directory
mkdir -p "$TARGET_ABS"

# Get source path
SRC_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# 2. Safely acquire and copy agent directory structure
mkdir -p "$TARGET_ABS/.agents"

if [ -d "$SRC_DIR/.agents" ]; then
  echo "Using local source files from: $SRC_DIR"
  cp -R -n "$SRC_DIR/.agents/"* "$TARGET_ABS/.agents/"
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
  
  # Copy files
  cp -R -n "$EXTRACTED_DIR/.agents/"* "$TARGET_ABS/.agents/"
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

echo "=========================================================="
echo "   AAC V2 Installation Completed Successfully!            "
echo "   Run './helper.sh validate' in the target folder to test."
echo "=========================================================="
