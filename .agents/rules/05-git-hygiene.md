---
name: git-hygiene
description: Scratch isolation, secret scanning, and clean repository hygiene across platforms.
trigger: always_on
---

# Git Hygiene, Scratch Isolation & Security Boundaries

- **Scratch Isolation**: All temporary scripts, scratch experiments, and notes MUST be placed inside `.agents/scratch/`. Never leave scratch files in root or source directories.
- **Zero Secret Exposure**: Never hardcode API keys, private keys, or tokens in tracked files. Reference credentials strictly via environment variables.
- **Cross-Platform Safety**: Ensure commands, path separators, and line endings function correctly across Linux, macOS, and Windows.
- **Conventional Commits**: Write atomic, clear commit messages following Conventional Commits format (`feat:`, `fix:`, `refactor:`, `test:`).
