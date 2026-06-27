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

# 2. Copy .agents directory content safely
echo "Copying agent directory structure and skills..."
mkdir -p "$TARGET_ABS/.agents"

# Copy directories recursively. Use -n (no-clobber) where supported or copy folder structure
# We copy core files, ensuring we don't overwrite user's existing work if installing in an existing project
cp -R -n "$SRC_DIR/.agents/"* "$TARGET_ABS/.agents/"

# Copy CLI wrappers
cp -n "$SRC_DIR/helper.sh" "$TARGET_ABS/helper.sh" || true
cp -n "$SRC_DIR/helper.ps1" "$TARGET_ABS/helper.ps1" || true
chmod +x "$TARGET_ABS/helper.sh"

# Copy root rules file if not existing
if [ ! -f "$TARGET_ABS/AGENTS.md" ]; then
  cp "$SRC_DIR/AGENTS.md" "$TARGET_ABS/AGENTS.md"
  echo "Created AGENTS.md."
else
  echo "AGENTS.md already exists. Skipping overwrite to preserve host project files."
fi

# 3. Initialize Git if not present in target
if [ ! -d "$TARGET_ABS/.git" ]; then
  echo "Initializing empty Git repository in target directory..."
  git -C "$TARGET_ABS" init
fi

# 4. Execute bootstrapping and synchronization in target directory
echo "Configuring environment in target directory..."
cd "$TARGET_ABS"

# Execute bootstrap.sh from source
bash "$SRC_DIR/bootstrap.sh"

# Run sync tool via CLI wrapper to align skills and memory registers
./helper.sh sync

echo "=========================================================="
echo "   AAC V2 Installation Completed Successfully!            "
echo "   Run './helper.sh validate' in the target folder to test."
echo "=========================================================="
