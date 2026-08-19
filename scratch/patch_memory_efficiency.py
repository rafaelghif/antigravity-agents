from pathlib import Path
import re

for p in Path('.agents/agents').glob('*.md'):
    content = p.read_text(encoding='utf-8')
    content = re.sub(
        r'1\. \*\*Memory & Skill Injection\*\*: You MUST execute `view_file` on `\.agents/brain/rules\.md` \(if it exists\) to load Procedural Memory, and (.*) BEFORE',
        r'1. **Context & Skill Injection**: You MUST execute `grep_search` on `.agents/brain/rules.md` using keywords from your task (DO NOT read the whole file), and execute `view_file` on \1 BEFORE',
        content
    )
    content = re.sub(
        r'1\. \*\*Memory & Skill Injection\*\*: You MUST use `view_file` to read `\.agents/brain/rules\.md` \(if it exists\) to load Procedural Memory, and (.*) BEFORE',
        r'1. **Context & Skill Injection**: You MUST execute `grep_search` on `.agents/brain/rules.md` using keywords from your task (DO NOT read the whole file), and execute `view_file` on \1 BEFORE',
        content
    )
    p.write_text(content, encoding='utf-8')

# Fix AGENTS.md rule 9
agents_path = Path('AGENTS.md')
agents_content = agents_path.read_text(encoding='utf-8')
agents_content = re.sub(
    r'9\. \[SELF_LEARNING\] You MUST maintain Procedural Memory.*?All subagents will inherit this memory\.',
    r'9. [SELF_LEARNING] Maintain hyper-dense Procedural Memory in `.agents/brain/rules.md`. If you learn a lesson, append it. If the file exceeds 50 lines, you MUST compact/prune obsolete rules to save context tokens.',
    agents_content
)
agents_content = agents_content.replace(
    "0. Load Memory (`view_file` `.agents/brain/rules.md` if it exists).",
    "0. Load Memory (use `grep_search` on `.agents/brain/rules.md` for keywords)."
)
agents_path.write_text(agents_content, encoding='utf-8')
