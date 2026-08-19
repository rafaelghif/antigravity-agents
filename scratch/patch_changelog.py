import re

with open("CHANGELOG.md", "r") as f:
    content = f.read()

# Remove the incorrectly appended release notes at the end
content = re.sub(r'# v4\.4\.20 - Anti-Yes-Man & Procedural Memory.*?Subagent Consistency.*?\n', '', content, flags=re.DOTALL)

# Insert the new release notes right after the Changelog header
new_release = """## [4.4.20] - 2026-08-19

### Features
- **[SELF_LEARNING]**: Activated the Procedural Memory engine. All subagents are now forced to inject `.agents/brain/rules.md` before execution to establish long-term learning.
- **Anti-Yes-Man Persona**: Agents will now aggressively push back against suboptimal architectures instead of blindly agreeing.
- **Semantic Grapher Tests**: Added full test coverage for the AST parser (`scripts/semantic_grapher.py`) ensuring stability for Python, TS, and Go AST extraction.
- **Subagent Consistency**: Implemented `<ENTERPRISE_STANDARDS>` across all skills and enforced mandatory memory injection across all subagent protocols.

"""

content = content.replace("# Changelog\n\n", "# Changelog\n\n" + new_release)

with open("CHANGELOG.md", "w") as f:
    f.write(content)
