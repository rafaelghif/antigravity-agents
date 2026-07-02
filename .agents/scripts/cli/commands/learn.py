import os
import sys
import re
import subprocess
from datetime import datetime

DIAGNOSTIC_RULES = [
    {
        "id": "mock_testing",
        "category": "Testing / Mocking",
        "keywords": [r"mock", r"unittest\.mock", r"pytest", r"side_effect", r"MagicMock", r"patch\("],
        "file_patterns": [r"test_.*\.py", r"tests/"],
        "suggested_lesson": "Ensure mock side effects are isolated and sys.exit mocks raise SystemExit to prevent uncontrolled test discovery side-effects."
    },
    {
        "id": "schema",
        "category": "Database Schema",
        "keywords": [r"schema", r"model", r"database", r"ForeignKey", r"Column"],
        "file_patterns": [r"schema\.md", r"schema\.json", r"models?\.py"],
        "suggested_lesson": "Strictly align API and database models with the project schemas to maintain interface integrity."
    },
    {
        "id": "path_handling",
        "category": "Path Handling / OS Compatibility",
        "keywords": [r"os\.path", r"pathlib", r"abspath", r"replace\(['\"]\\\\['\"],\s*['\"]/['\"]\)", r"dirname", r"__file__"],
        "file_patterns": [],
        "suggested_lesson": "Use cross-platform path resolution helpers instead of hardcoded OS separators to prevent Windows/Linux path mismatches."
    },
    {
        "id": "shell_scripting",
        "category": "Shell Scripting",
        "keywords": [r"set -euo pipefail", r"ExecutionPolicy", r"BASH_SOURCE"],
        "file_patterns": [r"\.sh$", r"\.ps1$", r"\.bat$"],
        "suggested_lesson": "Maintain parity between Bash (.sh) and PowerShell (.ps1) helper scripts for consistent developer experience across platforms."
    },
    {
        "id": "token_optimization",
        "category": "Context / Token Optimization",
        "keywords": [r"token", r"context", r"active_context", r"view_file"],
        "file_patterns": [r"context\.py", r"active_context\.md"],
        "suggested_lesson": "Use targeted context optimization to minimize prompt token footprint while preserving compliance with rules."
    },
    {
        "id": "git_profiles",
        "category": "Git Profile & Credentials",
        "keywords": [r"git_profiles", r"GPG", r"ssh-key", r"signingkey"],
        "file_patterns": [r"profile\.py", r"git_profiles\.json"],
        "suggested_lesson": "Validate GPG key imports and developer identity rotation rules locally to safeguard credentials."
    }
]

def analyze_diff(base_branch="main"):
    """
    Analyzes git diff between base_branch and HEAD/working-tree.
    Returns list of suggested (category, lesson) tuples.
    """
    try:
        # Get diff of commits and unstaged changes on feature branch relative to base_branch
        res = subprocess.run(
            ['git', 'diff', f'{base_branch}...'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            # Fallback to simple diff if three-dot is not supported or errors
            res = subprocess.run(
                ['git', 'diff', base_branch],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res.returncode != 0:
                return []
        
        diff_text = res.stdout
        
        # Get list of changed files
        res_files = subprocess.run(
            ['git', 'diff', '--name-only', f'{base_branch}...'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        changed_files = res_files.stdout.splitlines() if res_files.returncode == 0 else []
        
        suggestions = []
        for rule in DIAGNOSTIC_RULES:
            match_found = False
            
            # Check file patterns
            if rule["file_patterns"]:
                for fp in rule["file_patterns"]:
                    for f in changed_files:
                        if re.search(fp, f, re.IGNORECASE):
                            # File match found, now check if keywords are also in the diff
                            for kw in rule["keywords"]:
                                if re.search(kw, diff_text, re.IGNORECASE):
                                    match_found = True
                                    break
                            if match_found:
                                break
                    if match_found:
                        break
            else:
                # No file patterns, check keywords globally in the diff
                for kw in rule["keywords"]:
                    if re.search(kw, diff_text, re.IGNORECASE):
                        match_found = True
                        break
            
            if match_found:
                suggestions.append((rule["category"], rule["suggested_lesson"]))
                
        return suggestions
    except Exception as e:
        print(f"Warning: Diff analysis encountered an error: {e}")
        return []

def record_lesson(lesson: str, category: str = None):
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
        
    # Prevent duplicate lessons from accumulating
    if lesson in content:
        print(f"[INFO] Lesson already exists in '{lessons_path}'. Skipping recording.")
        return
        
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

def extract_lessons_from_commits(base_branch="main"):
    """
    Extracts lessons from commits on the current feature branch since base_branch.
    Looks for commit messages or descriptions that contain explicit lessons.
    Format:
    - Commits with prefix "lesson:" or containing "Learning:" or similar.
    """
    try:
        # Get commit hashes and subjects/bodies on feature branch relative to base_branch
        res = subprocess.run(
            ['git', 'log', f'{base_branch}..HEAD', '--format=%s%n%b'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            return []
            
        commit_text = res.stdout
        lessons = []
        # Find lines like:
        # - lesson: description
        # - Learning: description
        # - [Learning: Category] description
        pattern = r'(?m)^\s*[-*]?\s*(?:lesson|learning|learn):\s*(.*)$'
        for match in re.finditer(pattern, commit_text, re.IGNORECASE):
            lesson_text = match.group(1).strip()
            if lesson_text:
                lessons.append(("Git Commit", lesson_text))
                
        # Also check for lines starting with "Learning:" or "[Learning:"
        pattern_bracket = r'(?m)^\s*[-*]?\s*\[?Learning:\s*([^\]\n]+)\]?:?\s*(.*)$'
        for match in re.finditer(pattern_bracket, commit_text, re.IGNORECASE):
            cat = match.group(1).strip()
            desc = match.group(2).strip()
            if desc:
                lessons.append((cat, desc))
            elif cat:
                lessons.append(("Git Commit", cat))
                
        return lessons
    except Exception as e:
        print(f"Warning: Commit analysis encountered an error: {e}")
        return []

def suggest_and_record_lessons(base_branch="main"):
    is_testing = "unittest" in sys.modules or "pytest" in sys.modules or os.environ.get("AAC_TEST_MODE") == "1"
    is_non_interactive = not sys.stdin.isatty() or ((os.getenv("ANTIGRAVITY_AGENT") == "1" or os.getenv("ANTIGRAVITY_NONINTERACTIVE") == "1") and not is_testing)
    if is_non_interactive:
        print("🧠 [LEARN] Auto-Lessons Extractor: Non-interactive mode detected. Auto-extracting lessons...")
        # 1. Analyze git diff for matches
        suggestions = analyze_diff(base_branch)
        
        # 2. Extract lessons from commits
        commit_lessons = extract_lessons_from_commits(base_branch)
        
        recorded_count = 0
        recorded_lessons = set() # Avoid duplicates
        
        # Record matched diff suggestions
        for cat, lesson in suggestions:
            if lesson not in recorded_lessons:
                record_lesson(lesson, cat)
                recorded_lessons.add(lesson)
                recorded_count += 1
                
        # Record commit lessons
        for cat, lesson in commit_lessons:
            if lesson not in recorded_lessons:
                record_lesson(lesson, cat)
                recorded_lessons.add(lesson)
                recorded_count += 1
                
        if recorded_count == 0:
            print("[INFO] No auto-extractable lessons matched or found in commits.")
        else:
            print(f"[OK] Successfully auto-recorded {recorded_count} lessons learned.")
        return
        
    print("\n🧠 [LEARN] Auto-Lessons Extractor: Analyzing git diff for lessons learned...")
    suggestions = analyze_diff(base_branch)
    
    options = []
    for cat, lesson in suggestions:
        options.append({"category": cat, "lesson": lesson})
        
    print("\nBased on your changes, here are the suggested lessons learned:")
    idx = 1
    for opt in options:
        print(f"  {idx}. [{opt['category']}] {opt['lesson']}")
        idx += 1
    print(f"  {idx}. [Custom] Enter your own lesson learned note.")
    print(f"  {idx+1}. [Skip] Do not record any lesson learned.")
    
    try:
        choice = input(f"\nSelect an option (1-{idx+1}): ").strip()
        if not choice:
            print("No option selected. Skipping.")
            return
        choice_idx = int(choice)
    except (ValueError, KeyboardInterrupt, EOFError):
        print("\nSkipping lesson learned extraction.")
        return
        
    if choice_idx < 1 or choice_idx > idx + 1:
        print("Invalid option. Skipping lesson learned extraction.")
        return
        
    if choice_idx <= len(options):
        selected = options[choice_idx - 1]
        record_lesson(selected["lesson"], selected["category"])
    elif choice_idx == idx:
        try:
            custom_lesson = input("Enter your custom lesson: ").strip()
            if not custom_lesson:
                print("Empty lesson. Skipping.")
                return
            custom_category = input("Enter category (optional): ").strip()
            record_lesson(custom_lesson, custom_category if custom_category else None)
        except (KeyboardInterrupt, EOFError):
            print("\nSkipping custom lesson learned.")
            return
    else:
        print("Skipped recording lesson learned.")

def run(args):
    if len(args) == 0:
        print("Usage: helper.sh learn \"<lesson learned content>\" [--category <category>]")
        print("       helper.sh learn --from-diff [--base <branch>]")
        sys.exit(1)
        
    if args[0] == "--from-diff":
        base_branch = "main"
        if len(args) > 2 and args[1] == "--base":
            base_branch = args[2]
        else:
            # Detect master vs main
            res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_master.returncode == 0:
                base_branch = "master"
        suggest_and_record_lessons(base_branch)
        return
        
    lesson = args[0]
    category = None
    
    # Parse optional category
    if len(args) > 2 and args[1] == "--category":
        category = args[2]
    elif len(args) > 1 and not args[1].startswith("-"):
        category = args[1]
        
    record_lesson(lesson, category)
