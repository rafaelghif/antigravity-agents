# Antigravity Agent Core VS Code Integration

This is a local, lightweight integration extension template to connect VS Code & Cursor IDE directly with the Antigravity Agent Core V2 workspace command helpers.

## Features
* **Git Profile Status Bar Widget**: Shows active GPG/SSH rotation identity at the bottom and allows switching with one click.
* **Module Locking Integration**: Lock files directly via VS Code Command Palette.

## Installation
1. Open VS Code or Cursor.
2. Press `F5` while opening this folder inside VS Code to launch a Developer Extension Host instance with the extension running.
3. To package the extension: run `npx -y vsce package` inside this directory to compile a `.vsix` file and install manually via **Install from VSIX** in VS Code.
