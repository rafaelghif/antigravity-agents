# Task Workflow: Implement Interactive ADR Wizard Skill

This task implements the Interactive ADR Wizard skill and integrates it into the helper CLI and validation hooks.

## 1. Architectural Decisions & Specifications
- **Skill Directory**: `.agents/skills/adr-wizard/`
- **Command Redirect**: `helper.sh adr-wizard` forwards arguments to `python3 .agents/skills/adr-wizard/scripts/main.py`.
- **Dual-Mode Execution**:
  - **Interactive Mode**: If no arguments are provided and stdin is a TTY, prompt the developer step-by-step for Title, Status, Context, Decision, and Consequences.
  - **Non-Interactive Mode**: Accept command-line arguments: `--title`, `--status`, `--context`, `--decision`, `--consequences`, or `--json <path>`.
- **Validation Gates**:
  - **Sequential Sequence**: Verify no numeric gaps in `adrs/` filenames (001, 002, 003...).
  - **Bidirectional Sync**: Every file must be in `.agents/adr.md` index and vice-versa.
  - **Content Checks**: Context, Decision, and Consequences sections must not be empty or contain default template placeholders.
  - Integrate these checks directly into `validate.sh` (upgrading Check 10).

## 2. Checklist & Implementation Status

- [x] **Scaffold Skill & CLI Registration**
  - [x] Lock module `adr-wizard` by running `./.agents/scripts/helper.sh lock adr-wizard`
  - [x] Run `./.agents/scripts/helper.sh create-skill adr-wizard "Interactive Architectural Decision Record guided wizard"`
  - [x] Register `adr-wizard` command in `.agents/scripts/cli/commands/adr_wizard.py` and forward parameters
  - [x] Add CLI delegation in `.agents/scripts/cli/helper.py`
- [x] **Wizard Script Implementation**
  - [x] Implement interactive shell prompts using `input()` with defaults
  - [x] Implement non-interactive flag inputs (argparse)
  - [x] Implement ADR file creation & auto-indexing to `.agents/adr.md`
- [x] **Validation Enhancements**
  - [x] Implement sequence, sync, and content validators in `.agents/scripts/cli/commands/validate.py` or `validate.sh`
  - [x] Verify that invalid ADRs are blocked by `helper.sh validate`
- [x] **Verification & Validation**
  - [x] Run new unit tests `python3 tests/test_rotation.py`
  - [x] Perform validation check `./.agents/scripts/helper.sh validate`
  - [x] Commit changes via helper script
