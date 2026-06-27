import os
import sys
from datetime import datetime

def run(args):
    if len(args) == 0:
        print("Usage: helper.sh learn \"<lesson learned content>\" [--category <category>]")
        sys.exit(1)
        
    lesson = args[0]
    category = None
    
    # Parse optional category
    if len(args) > 2 and args[1] == "--category":
        category = args[2]
    elif len(args) > 1 and not args[1].startswith("-"):
        category = args[1]
        
    lessons_path = ".agents/memory/lessons-learned.md"
    if not os.path.exists(".agents/memory"):
        os.makedirs(".agents/memory", exist_ok=True)
        
    if not os.path.exists(lessons_path):
        # Bootstrap lessons-learned.md if missing
        with open(lessons_path, 'w', encoding='utf-8') as f:
            f.write("# AAC V2 Lessons Learned\n\nThis file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.\n\n## Lessons Learned\n")
            
    # Read the current content
    with open(lessons_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Append the lesson to the list under ## Lessons Learned
    date_str = datetime.now().strftime("%Y-%m-%d")
    prefix = f"**{category}**: " if category else ""
    new_bullet = f"- **[{date_str}]** {prefix}{lesson}\n"
    
    # Insert right under ## Lessons Learned header
    header_marker = "## Lessons Learned"
    idx = content.find(header_marker)
    if idx != -1:
        insert_pos = idx + len(header_marker)
        # Find next newline or just append right after
        nl_pos = content.find('\n', insert_pos)
        if nl_pos != -1:
            updated_content = content[:nl_pos+1] + new_bullet + content[nl_pos+1:]
        else:
            updated_content = content + "\n" + new_bullet
    else:
        updated_content = content + f"\n## Lessons Learned\n{new_bullet}"
        
    with open(lessons_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
        
    print(f"[OK] Successfully recorded lesson: \"{lesson}\" in '{lessons_path}'.")
