# Task Workflow: Modernize CLI TUI Dashboard UX

This task modernizes the console dashboard menu (TUI) to make it visually attractive, modern, and highly intuitive for non-technical users. It uses ANSI colors, clean card-like borders, status indicators, and clear plain-English labels.

## 1. Architectural Decisions & Mappings
- **Target File**: [menu.py](file://../../.agents/scripts/cli/commands/menu.py)
- **Visual Improvements**:
  - **ANSI Styling**: Add bright colors (Cyan, Green, Magenta, Yellow) to separate categories.
  - **Plain-English Explanations**: Change jargon to descriptive actions (e.g. "Lock folder" instead of "Lock module").
  - **Dynamic Status Dashboard**:
    - Show active branch and email in a prominent colored card.
    - Display locks status with a clear warning if locked.
    - Display a visual ASCII progress bar for token budget (e.g., `[██░░░░░░░░] 20%`).
  - **ANSI Auto-Detection**: Ensure colors are disabled if the output is piped or not a TTY to prevent raw escape codes in logs.

---

## 2. Implementation Checklist

- [x] **Lock CLI Module**
  - Run `./.agents/scripts/helper.sh lock cli`
- [x] **Implement ANSI and Layout Upgrades in `menu.py`**
  - Create color coding helper, add dashboard progress bar, and rewrite menu texts in [menu.py](file://../../.agents/scripts/cli/commands/menu.py).
- [x] **Verify and Test**
  - Run tests (`test_menu_command.py`) and fix mocks if they are affected by the new stdout prints.
  - Launch helper TUI and preview.
- [x] **Release locks & Commit**
  - Compile `bootstrap.sh` using `scratch/compile_bootstrap.py`.
  - Run `./.agents/scripts/helper.sh commit feat cli "modernize interactive CLI dashboard with colors and progress indicators"`
