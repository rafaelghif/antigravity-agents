#!/usr/bin/env bash
# POSIX-compliant installer for Antigravity Agent Core (AAC) V3
set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_ABS=$(realpath "$TARGET_DIR")

# 0. Check for Git presence
if ! command -v git &>/dev/null; then
  echo "=========================================================="
  echo "   [ERROR] Git is not installed!"
  echo "=========================================================="
  echo "Git is required to pull repository data, rotate profiles, and track version control."
  echo "Please install Git (from https://git-scm.com or via your package manager)"
  echo "and run the installer again."
  echo "Installation aborted."
  echo "=========================================================="
  exit 1
fi

# 0. Check for Python 3 presence
PYTHON_EXEC=""
if command -v python3 &>/dev/null; then
  PYTHON_EXEC="python3"
elif command -v python &>/dev/null; then
  if python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_EXEC="python"
  fi
fi

if [ -z "$PYTHON_EXEC" ]; then
  echo "=========================================================="
  echo "   [ERROR] Python 3 is not installed!"
  echo "=========================================================="
  echo "Python 3 is required to run the Antigravity Agent Core CLI and validation hooks."
  echo "If you do not install Python 3, the agent cannot function."
  echo "Please install Python 3 (from https://www.python.org or via your package manager)"
  echo "and run the installer again."
  echo "Installation aborted."
  echo "=========================================================="
  exit 1
else
  # Verify minimum Python version >= 3.8
  PYTHON_VERSION=$("$PYTHON_EXEC" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
  MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
  if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]; }; then
    echo "=========================================================="
    echo "   [ERROR] Python version $PYTHON_VERSION is too old!"
    echo "=========================================================="
    echo "AAC V3 requires Python 3.8 or newer. Found Python $PYTHON_VERSION."
    echo "Please upgrade Python and run the installer again."
    echo "Installation aborted."
    echo "=========================================================="
    exit 1
  fi
fi

echo "=========================================================="
echo "   Installing Antigravity Agent Core V3..."
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
SRC_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ]; then
  SRC_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
fi

# 2. Safely acquire and copy agent directory structure
mkdir -p "$TARGET_ABS/.agents"

echo "Downloading Antigravity Agent Core from GitHub..."
  
  # Verifying network connection to GitHub via Git
  echo "Verifying network connection to GitHub..."
  REPO_URL="${AAC_SOURCE_REPO:-https://github.com/rafaelghif/antigravity-agents.git}"
  if ! git ls-remote "$REPO_URL" HEAD &>/dev/null; then
    echo "=========================================================="
    echo "   [ERROR] GitHub Connection Failed!"
    echo "=========================================================="
    echo "An active internet connection is required to download the Antigravity Agent Core"
    echo "source files from GitHub."
    echo "Please check your network connection and try again."
    echo "Installation aborted."
    echo "=========================================================="
    exit 1
  fi

  # Create a temporary directory
  TEMP_DIR=$(mktemp -d)
  
  echo "Cloning Antigravity Agent Core repository from Git..."
  if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" &>/dev/null; then
    echo "=========================================================="
    echo "   [ERROR] Git Clone Failed!"
    echo "=========================================================="
    echo "Failed to clone from $REPO_URL."
    echo "Please check your network connection and try again."
    echo "Installation aborted."
    echo "=========================================================="
    rm -rf "$TEMP_DIR"
    exit 1
  fi
  
  EXTRACTED_DIR="$TEMP_DIR/repo"
  
  # Copy files recursively excluding __pycache__, locks.json, git_profiles.json, .DS_Store, *.pyc
  (
    cd "$EXTRACTED_DIR"
    find .agents -type f \
      ! -path "*/__pycache__/*" \
      ! -path "*/.git/*" \
      ! -name "git_profiles.json" \
      ! -name "projects.json" \
      ! -name "locks.json" \
      ! -name "rules.md" \
      ! -name ".DS_Store" \
      ! -name "*.pyc" \
      ! -name "*.pyo" \
      ! -path ".agents/memory/*" \
      ! -path ".agents/tasks/*" \
      ! -path ".agents/issues/*" \
      ! -path ".agents/plans/*" \
      ! -path ".agents/tests/*" \
      ! -path ".agents/archive/*" \
      ! -path ".agents/logs/*" \
      ! -path ".agents/state/*" \
      ! -name "active_context.md" \
      ! -name "token_budget.json" \
      ! -name "sync_cache.json" \
      ! -name "cooldowns.json" \
      ! -name "upgrade_state.json" \
      ! -name "schema.md" \
      ! -name "api_keys" \
      ! -name "active_api_keys" \
      ! -name "active_api_keys.ps1" \
      ! -name "active_api_profile_name" \
      -exec sh -c '
        for file; do
          dest_file="'"$TARGET_ABS"'/$file"
          mkdir -p "$(dirname "$dest_file")"
          cp "$file" "$dest_file" 2>/dev/null || true
        done
      ' _ {} +
  )
  
  # Initialize clean memory folder in target
  mkdir -p "$TARGET_ABS/.agents/memory/decisions"
  mkdir -p "$TARGET_ABS/.agents/memory/blueprints"
  if [ -d "$EXTRACTED_DIR/.agents/memory/blueprints" ]; then
    cp -r "$EXTRACTED_DIR/.agents/memory/blueprints/"* "$TARGET_ABS/.agents/memory/blueprints/" 2>/dev/null || true
  fi
  if [ -d "$EXTRACTED_DIR/.agents/memory/templates" ]; then
    for t in "$EXTRACTED_DIR/.agents/memory/templates/"*.template; do
      [ -f "$t" ] || continue
      filename_t=$(basename "$t" .template)
      cp -n "$t" "$TARGET_ABS/.agents/memory/$filename_t"
    done
  fi

  # Copy projects.example to projects.json if it doesn't exist
  if [ -f "$EXTRACTED_DIR/.agents/projects.example" ] && [ ! -f "$TARGET_ABS/.agents/projects.json" ]; then
    cp "$EXTRACTED_DIR/.agents/projects.example" "$TARGET_ABS/.agents/projects.json" || true
  fi

  cp "$EXTRACTED_DIR/helper.sh" "$TARGET_ABS/helper.sh" || true
  cp "$EXTRACTED_DIR/helper.ps1" "$TARGET_ABS/helper.ps1" || true
  
  
  # Run bootstrap.sh from extracted folder inside target folder context
  (cd "$TARGET_ABS" && bash "$EXTRACTED_DIR/bootstrap.sh")
  
  # Cleanup
  rm -rf "$TEMP_DIR"

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
echo "   AAC V3 Installation Completed Successfully!            "
echo "   Run './helper.sh validate' in the target folder to test."
echo "=========================================================="
