import sys
import os
import re
import json
import subprocess
from typing import List, Dict, Any

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def get_current_branch() -> str:
    res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
    return res.stdout.strip() if res.returncode == 0 else ""

def get_issue_id(branch: str) -> str:
    match = re.search(r'(issue|task|chore)-[0-9]+', branch, re.IGNORECASE)
    if match:
        return match.group(0).lower()
    # Support direct feat/123 or fix/123 format
    match = re.search(r'(feat|fix|chore|docs)/([0-9]+)', branch, re.IGNORECASE)
    if match:
        return f"issue-{match.group(2)}"
    return ""

def parse_yaml_frontmatter(content: str) -> Dict[str, str]:
    meta = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta

def get_issue_details(issue_id: str) -> Dict[str, Any]:
    file_id = issue_id.replace('-', '_')
    # 1. Search in active issues first
    issue_file = f".agents/issues/{file_id}.md"
    if not os.path.exists(issue_file):
        # 2. Fallback to archive issues
        issue_file = f".agents/archive/issues/{file_id}.md"

    details = {
        "title": "Unknown Title",
        "tasks": [],
        "description": "No description found."
    }
    if os.path.exists(issue_file):
        with open(issue_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meta = parse_yaml_frontmatter(content)
        details["title"] = meta.get("title", "Unknown Title")
        
        tasks = []
        in_problem_statement = False
        problem_text = []
        for line in content.split('\n'):
            if line.strip().startswith('## Problem Statement'):
                in_problem_statement = True
                continue
            elif line.strip().startswith('## Tasks') or (in_problem_statement and line.strip().startswith('## ')):
                in_problem_statement = False
                
            if in_problem_statement and line.strip():
                problem_text.append(line.strip())
                
            if line.strip().startswith('- ['):
                tasks.append(line.strip())
        details["tasks"] = tasks
        details["description"] = " ".join(problem_text) if problem_text else ""
    return details

def get_locked_modules(branch: str) -> List[str]:
    try:
        try:
            from lock import load_locks
        except ImportError:
            from commands.lock import load_locks
        locks = load_locks()
        return [mod for mod, b in locks.items() if b == branch]
    except Exception as e:
        print(f"Error loading locks: {e}")
        return []

def get_git_changes() -> List[str]:
    res = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return [line.strip() for line in res.stdout.strip().split('\n')]
    return []

def archive_completed_tasks_and_plans() -> None:
    """Scan the task board, find issues in the Done column, and move their
    corresponding markdown files from .agents/issues/ and .agents/plans/ to .agents/archive/."""
    board_file = ".agents/tasks/board.md"
    if not os.path.exists(board_file):
        return
        
    done_issues = set()
    try:
        with open(board_file, 'r', encoding='utf-8') as f:
            board_content = f.read()
        # Extract Done section
        done_match = re.search(r'## Done\n([\s\S]*?)(?:##|$)', board_content)
        if done_match:
            # Find all issue ids: <!-- id: issue-xxx -->
            for match in re.finditer(r'<!-- id:\s*(issue-[a-zA-Z0-9_-]+)\s*-->', done_match.group(1)):
                done_issues.add(match.group(1).lower())
    except Exception as e:
        print_err(f"Failed to read task board for archiving: {e}")
        return

    if not done_issues:
        return

    # Create archive directories
    archive_issues_dir = ".agents/archive/issues"
    archive_plans_dir = ".agents/archive/plans"
    os.makedirs(archive_issues_dir, exist_ok=True)
    os.makedirs(archive_plans_dir, exist_ok=True)

    archived_count = 0
    # Process issues
    issues_dir = ".agents/issues"
    if os.path.exists(issues_dir):
        for f_name in os.listdir(issues_dir):
            if not f_name.endswith(".md"):
                continue
            normalized_name = f_name.lower().replace('_', '-')
            for issue_id in done_issues:
                file_id = issue_id.replace('-', '-')
                if file_id in normalized_name:
                    src_path = os.path.join(issues_dir, f_name)
                    dest_path = os.path.join(archive_issues_dir, f_name)
                    try:
                        os.rename(src_path, dest_path)
                        archived_count += 1
                    except Exception as e:
                        print_err(f"Failed to archive issue file '{f_name}': {e}")

    # Process plans
    plans_dir = ".agents/plans"
    if os.path.exists(plans_dir):
        for f_name in os.listdir(plans_dir):
            if not f_name.endswith(".md"):
                continue
            normalized_name = f_name.lower().replace('_', '-')
            for issue_id in done_issues:
                if issue_id in normalized_name:
                    src_path = os.path.join(plans_dir, f_name)
                    dest_path = os.path.join(archive_plans_dir, f_name)
                    try:
                        os.rename(src_path, dest_path)
                        archived_count += 1
                    except Exception as e:
                        print_err(f"Failed to archive plan file '{f_name}': {e}")
                        
    if archived_count > 0:
        print_ok(f"Successfully archived {archived_count} completed task/plan files to '.agents/archive/'.")

def get_workflow_mode() -> str:
    """Retrieve the workspace workflow mode ('solo' or 'team') from .agents/config.json."""
    config_path = ".agents/config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                return cfg.get("workflow_mode", "team")
        except Exception:
            pass
    return "team"

def get_semantic_skills(text: str) -> List[str]:
    """Scan text for keywords and return a list of matching skill names."""
    SKILL_MAP = {
        "testing": ["test", "jest", "pytest", "mocha", "junit", "coverage", "mock", "tdd"],
        "devops-release": ["docker", "deploy", "pipeline", "ci/cd", "ci", "cd", "build", "nginx", "github actions", "kubernetes", "k8s", "release", "semver", "version bump", "installer"],
        "troubleshooting": ["bug", "error", "crash", "fix", "leak", "panic", "debug", "traceback", "exception", "fail"],
        "engineering-standards": ["feature", "add", "create", "implement", "build", "refactor", "clean", "solid", "slow", "optimize", "memory", "performance", "architecture", "legacy"],
        "task-management": ["spec", "plan", "checklist", "issue", "board", "task", "roadmap", "milestone", "grill-me"],
        "database-evolution": ["database", "table", "field", "schema", "model", "migration", "relation", "sql", "orm", "query", "index", "column"],
        "documentation": ["doc", "readme", "manual", "guide", "comment", "docstring", "api doc", "blueprint"],
        "security-compliance": ["security", "vulnerability", "audit", "cve", "auth", "token", "jwt", "oauth", "password", "hash", "secret", "license"]
    }
    
    text_lower = text.lower()
    matched_skills = set()
    
    for skill, keywords in SKILL_MAP.items():
        for kw in keywords:
            # Match word boundary to avoid false positives (e.g. matching 'ci' inside 'specific')
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                matched_skills.add(skill)
                break
                
    return sorted(list(matched_skills))


def optimize_context() -> None:
    # First, archive completed tasks and plans to keep LLM context clean
    archive_completed_tasks_and_plans()

    branch = get_current_branch()
    workflow_mode = get_workflow_mode()
    
    if workflow_mode == "solo":
        # Allow main/master branch, and allow arbitrary branches
        if not branch:
            branch = "main"
        issue_id = get_issue_id(branch) or "solo-workflow"
    else:
        if not branch or branch in ('main', 'master'):
            print_err("Cannot optimize context on base branch main/master. Checkout a feature branch first.")
            sys.exit(1)
            
        issue_id = get_issue_id(branch)
        if not issue_id:
            print_err(f"Branch '{branch}' does not contain a valid issue ID pattern (e.g. feat/issue-123).")
            sys.exit(1)
        
    details = get_issue_details(issue_id)
    if issue_id == "solo-workflow" and details.get("title") == "Unknown Title":
        details["title"] = "Solo Development Workflow"
        details["description"] = "Running in solo mode (locks and branch alignment audits bypassed)."
    locks = get_locked_modules(branch)
    changes = get_git_changes()
    
    locked_str = "\n".join(f"- `{l}`" for l in locks) if locks else "- *No modules locked. Run './helper.sh lock <module>' to lock.*"
    changes_str = "\n".join(f"- `{c}`" for c in changes) if changes else "- *No uncommitted changes.*"
    tasks_str = "\n".join(t for t in details["tasks"]) if details["tasks"] else "- *No tasks defined.*"
    
    # Read synthesized rules from .agents/rules.md
    synthesized_rules_str = "- *No synthesized rules found.*"
    rules_file = ".agents/rules.md"
    if os.path.exists(rules_file):
        try:
            with open(rules_file, 'r', encoding='utf-8') as rf:
                rules_content = rf.read()
            match = re.search(r'## 6\. Synthesized Rules \(Self-Learning Memory\)[\s\S]*$', rules_content)
            if match:
                # Get the content of this section, stripping empty lines
                section_content = match.group(0).replace('## 6. Synthesized Rules (Self-Learning Memory)', '').strip()
                if section_content:
                    synthesized_rules_str = section_content
        except Exception:
            pass
            
    # Extract semantic skills based on issue content
    issue_text = details.get("description", "") + "\n" + details.get("title", "")
    semantic_skills = get_semantic_skills(issue_text)
    
    skills_injected_str = ""
    if semantic_skills:
        skills_blocks = []
        for skill in semantic_skills:
            skill_path = f".agents/skills/{skill}/SKILL.md"
            if os.path.exists(skill_path):
                skills_blocks.append(f"- `view_file {skill_path}`")
        if skills_blocks:
            skills_injected_str = "\n\n## 📖 Recommended Playbooks\n*Based on your task keywords, you MUST read these playbooks using the view_file tool if you haven't already:*\n" + "\n".join(skills_blocks)

    context_content = f"""# 🎯 Active Workspace Context Manifest

> [!IMPORTANT]
> This manifest defines the strict task scope and active workspace files for the current session.
> You must strictly follow all non-negotiable rules in [AGENTS.md](file://{os.path.abspath("AGENTS.md")}) and rules in [.agents/rules.md](file://{os.path.abspath(".agents/rules.md")}).

## 🎫 Active Issue: {issue_id.upper()}
- **Title**: {details["title"]}
- **Branch**: `{branch}`

## 🔒 Locked Modules & Files to Edit
{locked_str}

## 📂 Git Status Changes
{changes_str}

## 📋 Active Task Checklist
{tasks_str}

## 🧠 Synthesized Rules (Self-Learning Memory)
{synthesized_rules_str}

## ⚠️ Scope Boundaries
- **Strict Scope**: Only edit the files listed under "Locked Modules & Files to Edit" or files relevant to the active issue.
- **NEVER** edit files outside this scope unless explicitly requested by the USER.{skills_injected_str}
"""
    
    context_file = ".agents/state/active_context.md"
    try:
        os.makedirs(os.path.dirname(context_file), exist_ok=True)
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_content)
        print_ok(f"Context manifest successfully optimized and written to '{context_file}'.")
    except Exception as e:
        print_err(f"Failed to write context manifest: {e}")
        sys.exit(1)

def run(args: List[str]) -> None:
    if not args or args[0].lower() != "optimize":
        print("Usage: helper.py context optimize")
        sys.exit(1)
        
    optimize_context()
    sys.exit(0)
