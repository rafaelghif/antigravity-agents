import os
import sys
import glob
import re
from datetime import datetime
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py create-adr <title> [proposed|accepted|superseded]", file=sys.stderr)
        sys.exit(1)
        
    title = args[1]
    status = args[2].lower() if len(args) > 2 else "proposed"
    
    if status not in ("proposed", "accepted", "superseded"):
        print("Error: Status must be one of: proposed, accepted, superseded", file=sys.stderr)
        sys.exit(1)
        
    status_cap = status.capitalize()
    adrs_dir = os.path.join(utils.get_agents_dir(), "adrs")
    os.makedirs(adrs_dir, exist_ok=True)
    
    # Determine next ADR number
    count = 1
    existing_files = glob.glob(os.path.join(adrs_dir, "[0-9][0-9][0-9]-*.md"))
    count = len(existing_files) + 1
    
    num = f"{count:03d}"
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    filename = os.path.join(adrs_dir, f"{num}-{slug}.md")
    
    adr_date = datetime.now().strftime("%Y-%m-%d")
    
    adr_content = f"""# ADR-{num}: {title}

- **Date**: {adr_date}
- **Status**: {status_cap}

## Context
[Describe the problem context and alternatives]

## Decision
[Describe the decision made]

## Consequences
[Describe the result and impact of this decision]
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(adr_content)
        
    index_file = os.path.join(utils.get_agents_dir(), "adr.md")
    if os.path.isfile(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        if "## 1. Architectural Decisions Index" not in index_content:
            if not index_content.endswith('\n'):
                index_content += '\n'
            index_content += "\n## 1. Architectural Decisions Index\n"
            
        if not index_content.endswith('\n'):
            index_content += '\n'
            
        index_content += f"- [ADR-{num}: {title}](file://./adrs/{num}-{slug}.md) - Status: {status_cap}\n"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
    print(f"Created ADR-{num} at {filename} and registered in {index_file}")
