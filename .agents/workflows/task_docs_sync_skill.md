# Task Workflow: Implement docs-sync Skill

This workflow maps the implementation steps for the `docs-sync` specialized agent skill.

## 1. Architectural Decisions & Mappings
- **Skill Name**: `docs-sync`
- **Goal**: Synchronize inline code docstrings and comments into existing markdown files between placeholders.
- **Placeholder Format**:
  ```markdown
  <!-- DOCS-SYNC:START(relative/path/to/file.py) -->
  ...
  <!-- DOCS-SYNC:END(relative/path/to/file.py) -->
  ```
- **Parsing**: Built-in python `ast` module.
- **Formatting**:
  - Class Name -> `#### Class: Name`
  - Function Signature -> `##### `def name(args) -> return_type``
  - Docstring -> Blockquoted body (`> docstring`)

---

## 2. Implementation Checklist

- [x] **Lock skills module**
  - Run `./.agents/scripts/helper.sh lock skills`
- [x] **Scaffold Skill**
  - Run `./.agents/scripts/helper.sh create-skill docs-sync "Synchronize inline code comments / docstrings with markdown documentation files."`
- [x] **Implement `main.py`**
  - Update `.agents/skills/docs-sync/scripts/main.py` with parsing and file updating logic.
- [x] **Create Unit Tests**
  - Create `tests/test_skill_docs_sync.py` to test the parsing and updating functionality.
- [x] **Verify and Validate**
  - Run `python3 -m unittest tests/test_skill_docs_sync.py`
  - Run `./.agents/scripts/helper.sh validate`
- [x] **Document Changes**
  - Update `CHANGELOG.md`
- [x] **Release Locks & Commit**
  - Run `./.agents/scripts/helper.sh commit feat cli "add docs-sync specialized skill for automated docstring synchronization"`
