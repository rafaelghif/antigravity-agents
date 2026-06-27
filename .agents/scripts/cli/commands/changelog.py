import os
import sys
import re

# Inject parent directory containing git_api
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import subprocess
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

def get_current_version() -> str:
    """Read the current version from AGENTS.md."""
    agents_path = "AGENTS.md"
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r"-\s+\*\*Version:\*\*\s*(\d+\.\d+\.\d+)", content)
        if match:
            return match.group(1)
    return "0.0.0"

def get_latest_changelog_version() -> Optional[str]:
    """Parse CHANGELOG.md to find the latest version header."""
    changelog_path = "CHANGELOG.md"
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r"^##\s+\[(\d+\.\d+\.\d+)\]", line)
                if match:
                    return match.group(1)
    return None

def get_boundary_commit(version: str) -> Optional[str]:
    """Find the commit hash that matches the release of the given version or the last release."""
    # 1. Try resolving via git tags (vX.Y.Z or X.Y.Z)
    for tag_fmt in (f"v{version}", version):
        try:
            res = subprocess.run(
                ['git', 'rev-parse', f'{tag_fmt}^{{commit}}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

    # 2. Fallback to grepping commits log
    try:
        # Search git log for chore(release): version or version string
        res = subprocess.run(
            ['git', 'log', f'--grep={version}', '--format=%H', '-n', '1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
            
        # Fallback to the latest release commit in history
        res = subprocess.run(
            ['git', 'log', '--grep=chore(release):', '--format=%H', '-n', '1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def get_commits_since(commit_hash: Optional[str]) -> List[Tuple[str, str]]:
    """Get all commits since the boundary commit hash."""
    commits = []
    try:
        cmd = ['git', 'log', '--format=%H|%s']
        if commit_hash:
            cmd.append(f"{commit_hash}..HEAD")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if '|' in line:
                    h, s = line.split('|', 1)
                    commits.append((h.strip(), s.strip()))
    except Exception as e:
        print(f"Error reading git commits: {e}", file=sys.stderr)
    return commits

def extract_issue_title(issue_id: str) -> Optional[str]:
    """Extract clean title from local issue markdown file."""
    normalized_id = issue_id.lower().replace('-', '_')
    issue_dir = ".agents/issues"
    if os.path.exists(issue_dir):
        for f_name in os.listdir(issue_dir):
            if normalized_id in f_name.lower().replace('-', '_') or issue_id.lower() in f_name.lower():
                path = os.path.join(issue_dir, f_name)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Match first header like '# Issue 022: Title' or '# Title'
                            match = re.match(r"^#\s+(?:Issue\s+\d+:\s*)?(.+)", line)
                            if match:
                                return match.group(1).strip()
                except Exception:
                    pass
    return None

def classify_from_local_issue(issue_id: str) -> Optional[str]:
    """Parse local issue metadata to classify the category of the issue (breaking, feat, fix, etc.)."""
    normalized_id = issue_id.lower().replace('-', '_')
    issue_dir = ".agents/issues"
    if os.path.exists(issue_dir):
        for f_name in os.listdir(issue_dir):
            if normalized_id in f_name.lower().replace('-', '_') or issue_id.lower() in f_name.lower():
                path = os.path.join(issue_dir, f_name)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 1. Parse title or problem statement to classify
                    title = ""
                    for line in content.splitlines():
                        match = re.match(r"^title:\s*(.+)", line)
                        if match:
                            title = match.group(1).strip().lower()
                            break
                    if not title:
                        # Fallback: check first heading
                        for line in content.splitlines():
                            match = re.match(r"^#\s+(.+)", line)
                            if match:
                                title = match.group(1).strip().lower()
                                break
                    
                    if title:
                        if "breaking" in title or "major" in title or "!" in title:
                            return "breaking"
                        if any(w in title for w in ("feat", "feature", "implement", "add", "support")):
                            return "feat"
                        if any(w in title for w in ("fix", "bug", "remediate", "error", "prevent", "leak", "resolve")):
                            return "fix"
                        if "docs" in title or "document" in title:
                            return "docs"
                        if "refactor" in title:
                            return "refactor"
                        if "test" in title:
                            return "test"
                        if "chore" in title:
                            return "chore"
                except Exception:
                    pass
    return None

def parse_conventional_commits(commits: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Parse commit messages, resolve local issue metadata, and prioritize classifications to ensure correct SemVer."""
    categories = {
        "breaking": [],
        "feat": [],
        "fix": [],
        "refactor": [],
        "docs": [],
        "chore": [],
        "test": [],
        "other": []
    }
    
    # Regex to check Conventional Commits format
    conv_regex = re.compile(r"^(feat|fix|chore|refactor|docs|test|style|perf)(?:\([^)]+\))?(!)?:\s+(.+)", re.IGNORECASE)
    # Regex to find task/issue reference
    issue_regex = re.compile(r"((?:issue|task)-\d+)", re.IGNORECASE)
    
    # Priority for sorting/prioritizing issue commit categories
    # breaking (4) > feat (3) > fix (2) > chore/refactor/docs/test (1) > other (0)
    type_priority = {
        "breaking": 4,
        "feat": 3,
        "fix": 2,
        "refactor": 1,
        "docs": 1,
        "chore": 1,
        "test": 1,
        "other": 0
    }
    
    parsed_issues = {}  # Map of {ISSUE_ID: [(priority_value, category_key, entry_text)]}
    standalone_commits = []  # List of (category_key, entry_text) for commits without issue IDs
    
    for h, s in commits:
        # Ignore Git infrastructure commits (merges and automated releases)
        s_lower = s.lower()
        if (s_lower.startswith("chore(git): merge") or 
            s_lower.startswith("merge branch") or 
            s_lower.startswith("merge ") or 
            s_lower.startswith("chore(release):")):
            continue
            
        match = conv_regex.match(s)
        issue_match = issue_regex.search(s)
        
        issue_id = issue_match.group(1).upper() if issue_match else None
        
        if match:
            ctype, is_breaking, desc = match.groups()
            ctype = ctype.lower()
            if ctype in ("style", "perf"):
                ctype = "chore"
                
            cat = "breaking" if is_breaking else ctype
            priority = type_priority.get(cat, 1)
            
            entry = desc
            if issue_id:
                clean_title = extract_issue_title(issue_id)
                if clean_title:
                    entry = f"{clean_title} ({issue_id})"
                else:
                    entry = f"{desc} ({issue_id})"
                    
                if issue_id not in parsed_issues:
                    parsed_issues[issue_id] = []
                parsed_issues[issue_id].append((priority, cat, entry))
            else:
                standalone_commits.append((cat, entry))
        else:
            # Fallback to general parsing
            entry = s
            cat = "other"
            priority = 0
            if issue_id:
                clean_title = extract_issue_title(issue_id)
                if clean_title:
                    entry = f"{clean_title} ({issue_id})"
                else:
                    entry = f"{s} ({issue_id})"
                
                # Check if local issue spec metadata can classify the category
                issue_cat = classify_from_local_issue(issue_id)
                if issue_cat:
                    cat = issue_cat
                    priority = type_priority.get(cat, 1)
                    
                if issue_id not in parsed_issues:
                    parsed_issues[issue_id] = []
                parsed_issues[issue_id].append((priority, cat, entry))
            else:
                standalone_commits.append((cat, entry))
                
    # Deduplicate issues by selecting the commit with the highest SemVer priority
    for issue_id, items in parsed_issues.items():
        items.sort(key=lambda x: x[0], reverse=True)
        best_priority, best_cat, best_entry = items[0]
        categories[best_cat].append(best_entry)
        
    # Append standalone commits
    for cat, entry in standalone_commits:
        categories[cat].append(entry)
        
    return categories

def bump_semver(current: str, categories: Dict[str, List[str]]) -> str:
    """Calculate next semantic version based on commit categories."""
    major, minor, patch = map(int, current.split('.'))
    
    if categories["breaking"]:
        major += 1
        minor = 0
        patch = 0
    elif categories["feat"]:
        minor += 1
        patch = 0
    elif categories["fix"] or any(categories[c] for c in ("refactor", "docs", "chore", "test", "other")):
        patch += 1
        
    return f"{major}.{minor}.{patch}"

def update_version_in_files(old_version: str, new_version: str) -> None:
    """Update version strings in AGENTS.md, bootstrap.py, and bootstrap.sh."""
    # 1. Update AGENTS.md
    agents_path = "AGENTS.md"
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(
            r"-\s+\*\*Version:\*\*\s*" + re.escape(old_version),
            f"- **Version:** {new_version}",
            content
        )
        with open(agents_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Updated AGENTS.md version from {old_version} to {new_version}.")

    # 2. Update bootstrap.py
    bootstrap_py = ".agents/scripts/cli/commands/bootstrap.py"
    if os.path.exists(bootstrap_py):
        with open(bootstrap_py, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(
            r'AAC_VERSION\s*=\s*["\']' + re.escape(old_version) + r'["\']',
            f'AAC_VERSION = "{new_version}"',
            content
        )
        with open(bootstrap_py, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Updated bootstrap.py AAC_VERSION to {new_version}.")

    # 3. Update bootstrap.sh
    bootstrap_sh = "bootstrap.sh"
    if os.path.exists(bootstrap_sh):
        with open(bootstrap_sh, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(
            r"- \*\*Version:\*\* " + re.escape(old_version),
            f"- **Version:** {new_version}",
            content
        )
        # Also replace inside the inline Python block string replacement
        content = content.replace(f"- **Version:** {old_version}", f"- **Version:** {new_version}")
        with open(bootstrap_sh, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Updated bootstrap.sh version to {new_version}.")

def update_changelog(new_version: str, categories: Dict[str, List[str]]) -> None:
    """Prepend new version changes to CHANGELOG.md."""
    changelog_path = "CHANGELOG.md"
    if not os.path.exists(changelog_path):
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write("# Changelog\n\nAll notable changes to this project will be documented in this file.\n")
            
    # Format changes
    date_str = datetime.today().strftime('%Y-%m-%d')
    new_entry = f"\n## [{new_version}] - {date_str}\n"
    
    sections = [
        ("breaking", "💥 Breaking Changes"),
        ("feat", "🚀 Features"),
        ("fix", "🐛 Bug Fixes"),
        ("refactor", "🛠️ Refactors"),
        ("docs", "📝 Documentation"),
        ("chore", "⚙️ Chores"),
        ("test", "🧪 Tests"),
        ("other", "📋 Other Updates")
    ]
    
    has_content = False
    for key, title in sections:
        if categories[key]:
            has_content = True
            new_entry += f"\n### {title}\n"
            for item in categories[key]:
                new_entry += f"- {item}\n"
                
    if not has_content:
        new_entry += "\n- No notable changes.\n"
        
    with open(changelog_path, 'r', encoding='utf-8') as f:
        original = f.read()
        
    # Find insertion point right after main header
    header_end = original.find('\n', original.find('# Changelog')) + 1
    # Check if there is some description to skip
    if "documented in this file." in original:
        desc_end = original.find('documented in this file.') + len('documented in this file.')
        header_end = original.find('\n', desc_end) + 1
        
    updated_content = original[:header_end] + "\n" + new_entry + original[header_end:]
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"[OK] Prepended release changes to CHANGELOG.md.")
    return new_entry

def get_current_branch() -> Optional[str]:
    """Get the active Git branch name."""
    try:
        res = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None

def run(args: List[str]) -> None:
    preview = "--preview" in args
    bump_only = "--bump-only" in args
    
    print("==========================================================")
    print("   Antigravity Auto-Changelog & SemVer Generator         ")
    print("==========================================================")
    
    current_ver = get_current_version()
    latest_changelog_ver = get_latest_changelog_version()
    
    print(f"Current version (AGENTS.md): {current_ver}")
    print(f"Last version in CHANGELOG: {latest_changelog_ver or 'None'}")
    
    # Define boundary version
    boundary_ver = latest_changelog_ver or current_ver
    boundary_commit = get_boundary_commit(boundary_ver)
    
    if boundary_commit:
        print(f"Boundary commit found for version {boundary_ver}: {boundary_commit[:8]}")
    else:
        print(f"No boundary commit found for version {boundary_ver}. Parsing all commits.")
        
    commits = get_commits_since(boundary_commit)
    print(f"Found {len(commits)} commits since boundary.")
    
    categories = parse_conventional_commits(commits)
    
    # Inject current branch issue if not already present
    current_branch = get_current_branch()
    if current_branch and '/' in current_branch:
        parts = current_branch.split('/', 1)
        branch_type = parts[0].lower()
        branch_slug = parts[1]
        
        valid_types = ["breaking", "feat", "fix", "chore", "refactor", "docs", "test"]
        if branch_type in valid_types:
            # Normalize slug to issue ID (e.g. issue-047 or task-123)
            issue_match = re.search(r"(issue|task)-?\d+", branch_slug, re.IGNORECASE)
            if issue_match:
                match_val = issue_match.group(0)
                if '-' not in match_val:
                    match_val = re.sub(r"(\d+)", r"-\1", match_val)
                issue_id = match_val.upper()
                
                # Check if already resolved
                has_issue = False
                for cat, items in categories.items():
                    for item in items:
                        if issue_id in item:
                            has_issue = True
                            break
                            
                if not has_issue:
                    title = extract_issue_title(issue_id)
                    if title:
                        entry = f"{title} ({issue_id})"
                    else:
                        clean_desc = branch_slug.replace('-', ' ').title()
                        entry = f"{clean_desc} ({issue_id})"
                    
                    cat = branch_type
                    categories[cat].append(entry)
                    print(f"[INFO] Automatically injected issue entry from branch name: {entry}")
                    
    # Check if there are any changes in categories
    has_changes = any(categories[c] for c in categories)
    if not has_changes:
        print("No new commits or issue branch changes found. Nothing to update.")
        return
        
    new_ver = bump_semver(current_ver, categories)
    print(f"Calculated next version: {new_ver}")
    
    if preview:
        print("\n=== PREVIEW RELEASE NOTES ===")
        date_str = datetime.today().strftime('%Y-%m-%d')
        print(f"## [{new_ver}] - {date_str}")
        for k, lst in categories.items():
            if lst:
                print(f"\n### {k.capitalize()}")
                for item in lst:
                    print(f"- {item}")
        print("=============================")
        print("Preview mode active. No files were written.")
        return
        
    # Perform actual file writes
    update_version_in_files(current_ver, new_ver)
    
    entry_text = ""
    if not bump_only:
        entry_text = update_changelog(new_ver, categories)
        
    if entry_text:
        # Strip header (e.g. ## [2.14.0] - date) to form body
        body = entry_text.strip()
        header_line_end = body.find('\n')
        if header_line_end != -1:
            body = body[header_line_end:].strip()
            
        print("Publishing automated GitHub Release Draft...")
        try:
            import git_api
            release_url = git_api.create_github_release(
                tag_name=f"v{new_ver}",
                name=f"Release v{new_ver}",
                body=body,
                draft=True
            )
            if release_url:
                print(f"[OK] GitHub Draft Release created successfully: {release_url}")
        except Exception as e:
            print(f"[WARN] Failed to publish draft release to GitHub: {e}")
        
    print(f"\nRelease updates completed. Active version is now {new_ver}!")
