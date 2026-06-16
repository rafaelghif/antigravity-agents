import os
import sys
import re
from datetime import datetime
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py release <major|minor|patch>", file=sys.stderr)
        sys.exit(1)
        
    bump_type = args[1].lower()
    changelog_file = "CHANGELOG.md"
    
    if not os.path.exists(changelog_file):
        print("Error: CHANGELOG.md not found!", file=sys.stderr)
        sys.exit(1)
        
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract latest version
    m = re.search(r'^##\s+\[([0-9]+\.[0-9]+\.[0-9]+)\]', content, re.MULTILINE)
    if not m:
        print("Error: Could not parse current version from CHANGELOG.md.", file=sys.stderr)
        sys.exit(1)
        
    current_version = m.group(1)
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid bump type '{bump_type}'. Must be major, minor, or patch.", file=sys.stderr)
        sys.exit(1)
        
    next_version = f"{major}.{minor}.{patch}"
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Bumping version: {current_version} -> {next_version} ({bump_type})")
    
    # 1. Insert new version section at the top of version list (right before the first ## [version])
    # We find the first line starting with ## [version]
    lines = content.splitlines()
    new_lines = []
    inserted_version = False
    
    for line in lines:
        if line.startswith("## [") and not inserted_version:
            new_lines.append(f"## [{next_version}] - {current_date}")
            new_lines.append("### Added")
            new_lines.append("- ")
            new_lines.append("")
            inserted_version = True
        new_lines.append(line)
        
    # 2. Update version comparison links at the bottom (right before the first link mapping [version]: )
    content = "\n".join(new_lines)
    lines = content.splitlines()
    final_lines = []
    inserted_link = False
    repo_url = "https://github.com/rafaelghif/antigravity-agents"
    
    for line in lines:
        if re.match(r'^\[[0-9]+\.[0-9]+\.[0-9]+\]:', line) and not inserted_link:
            final_lines.append(f"[{next_version}]: {repo_url}/compare/v{current_version}...v{next_version}")
            inserted_link = True
        final_lines.append(line)
        
    new_content = "\n".join(final_lines)
    if not new_content.endswith('\n'):
        new_content += '\n'
        
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully bumped version to {next_version} and updated CHANGELOG.md.")
