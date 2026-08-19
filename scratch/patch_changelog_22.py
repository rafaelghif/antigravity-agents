import re
with open("CHANGELOG.md", "r") as f: content = f.read()
new_release = """## [4.4.22] - 2026-08-19

### Architecture
- **AST X-Ray Vision**: Resolved "Blind Refactoring" context limitations. Subagents (`planner`, `reviewer`) are now mandated to execute `semantic_grapher.py` to extract codebase AST maps *before* conducting impact analysis or multi-file refactors. This ensures no interconnected functions are missed while maintaining O(1) context efficiency.

"""
content = content.replace("# Changelog\n\n", "# Changelog\n\n" + new_release)
with open("CHANGELOG.md", "w") as f: f.write(content)
