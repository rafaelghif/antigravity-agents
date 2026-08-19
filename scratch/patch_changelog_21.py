import re

with open("CHANGELOG.md", "r") as f:
    content = f.read()

new_release = """## [4.4.21] - 2026-08-19

### Performance
- **Memory Compaction Engine**: Addressed token bloat by prohibiting subagents from loading the entirety of `rules.md` blindly. Agents are now mandated to use targeted `grep_search` to load context. 
- **Self-Pruning Memory**: Introduced a strict 50-line limit for `rules.md`. Agents must proactively rewrite and prune obsolete architectural lessons to conserve token bandwidth.

"""

content = content.replace("# Changelog\n\n", "# Changelog\n\n" + new_release)

with open("CHANGELOG.md", "w") as f:
    f.write(content)
