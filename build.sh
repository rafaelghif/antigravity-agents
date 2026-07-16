#!/usr/bin/env bash
set -euo pipefail

echo "Building standalone Antigravity Agent Core binary using PyInstaller..."

# Ensure pyinstaller is installed
if ! command -v pyinstaller &>/dev/null; then
    echo "PyInstaller not found. Installing requirements..."
    pip3 install -r requirements.txt
fi

# Determine OS
OS="$(uname -s)"
ARCH="$(uname -m)"

BINARY_NAME="aac-${OS}-${ARCH}"
if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    BINARY_NAME="aac-Windows-${ARCH}.exe"
fi

echo "Target binary: bin/${BINARY_NAME}"

# Clean previous builds
rm -rf build dist

# Compile the CLI helper entrypoint
# The entrypoint is .agents/scripts/cli/helper.py
pyinstaller --onefile \
    --name "${BINARY_NAME}" \
    --clean \
    --strip \
    .agents/scripts/cli/helper.py

mkdir -p bin
mv "dist/${BINARY_NAME}" bin/

echo "Build complete: bin/${BINARY_NAME}"
