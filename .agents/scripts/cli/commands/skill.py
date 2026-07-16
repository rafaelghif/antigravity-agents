import sys
import os
import shutil
import subprocess
import re
from typing import List

try:
    from . import validation
except ImportError:
    import validation

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SKILLS_DIR = ".agents/skills"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}", file=sys.stderr)

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def parse_skill_desc(skill_path: str) -> str:
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return "No SKILL.md found."
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        m_desc = re.search(r'description:\s*(.*?)\n', content)
        if m_desc:
            return m_desc.group(1).strip()
        return "No description provided."
    except Exception:
        return "Error reading description."

def handle_list() -> None:
    if not os.path.exists(SKILLS_DIR):
        print("No skills directory found.")
        return
    skills = []
    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if os.path.isdir(skill_path):
            desc = parse_skill_desc(skill_path)
            skills.append((skill_name, desc))
    
    if not skills:
        print("No custom skills installed.")
        return
        
    print("Installed Custom Skills:")
    for name, desc in sorted(skills):
        print(f"  - {GREEN}{name}{RESET}: {desc}")

def run_sync() -> None:
    # Trigger local sync.py module
    helper_dir = os.path.dirname(os.path.abspath(__file__))
    sync_script = os.path.abspath(os.path.join(helper_dir, "../../sync.py"))
    if os.path.exists(sync_script):
        import importlib.util
        spec = importlib.util.spec_from_file_location("sync_module", sync_script)
        sync_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync_module)
        sync_module.sync_skills_to_agents_md()
        print_ok("Synchronized AGENTS.md registry.")

def handle_install(source: str) -> None:
    if not source:
        print_err("Usage: helper.py skill install <source_path|git_url>")
        sys.exit(1)
        
    if not validation.validate_safe_path(source):
        print_err(f"Security Alert: Git URL or source path contains dangerous characters: {source}")
        sys.exit(1)
        
    os.makedirs(SKILLS_DIR, exist_ok=True)
    
    is_git = source.startswith("http://") or source.startswith("https://") or source.startswith("git@") or source.endswith(".git")
    
    if is_git:
        print(f"Cloning skill from Git: {source}...")
        import tempfile
        temp_dir = tempfile.mkdtemp()
        try:
            res = subprocess.run(['git', 'clone', '--depth', '1', source, temp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                print_err(f"Failed to clone Git repository: {res.stderr.decode('utf-8', errors='ignore')}")
                sys.exit(1)
            
            skill_sources = []
            if os.path.exists(os.path.join(temp_dir, "SKILL.md")):
                name = os.path.basename(source.rstrip("/").split("/")[-1])
                if name.endswith(".git"):
                    name = name[:-4]
                skill_sources.append((name, temp_dir))
            else:
                for item in os.listdir(temp_dir):
                    sub_p = os.path.join(temp_dir, item)
                    if os.path.isdir(sub_p) and os.path.exists(os.path.join(sub_p, "SKILL.md")):
                        skill_sources.append((item, sub_p))
                        
            if not skill_sources:
                print_err("No valid skill folder containing 'SKILL.md' was found in the repository.")
                sys.exit(1)
                
            for name, src_p in skill_sources:
                dest_p = os.path.join(SKILLS_DIR, name)
                if os.path.exists(dest_p):
                    shutil.rmtree(dest_p)
                shutil.copytree(src_p, dest_p)
                print_ok(f"Installed skill '{name}' under '{dest_p}'")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        source_path = os.path.abspath(source)
        if not os.path.exists(source_path):
            print_err(f"Local source path does not exist: {source_path}")
            sys.exit(1)
            
        if os.path.exists(os.path.join(source_path, "SKILL.md")):
            name = os.path.basename(source_path.rstrip("/"))
            dest_p = os.path.join(SKILLS_DIR, name)
            if os.path.exists(dest_p):
                shutil.rmtree(dest_p)
            shutil.copytree(source_path, dest_p)
            print_ok(f"Installed skill '{name}' under '{dest_p}'")
        else:
            print_err("Target folder does not contain 'SKILL.md'.")
            sys.exit(1)
            
    run_sync()

def handle_create(name: str, desc: str) -> None:
    if not name:
        print_err("Usage: helper.py skill create <skill_name> \"<description>\"")
        sys.exit(1)
        
    if not validation.validate_safe_identifier(name):
        print_err(f"Invalid skill name '{name}'. Only safe characters are allowed.")
        sys.exit(1)
    
    # Validate name format: lowercase letters, numbers, and hyphens only
    if not re.match(r'^[a-z0-9\-]+$', name):
        print_err("Invalid skill name. Only lowercase alphanumeric characters and hyphens are allowed.")
        sys.exit(1)
        
    dest_dir = os.path.join(SKILLS_DIR, name)
    if os.path.exists(dest_dir):
        print_err(f"Skill '{name}' already exists at {dest_dir}.")
        sys.exit(1)
        
    try:
        os.makedirs(dest_dir, exist_ok=True)
        skill_md_path = os.path.join(dest_dir, "SKILL.md")
        
        # Format the title nicely (convert kebab-case to title case)
        title = " ".join(word.capitalize() for word in name.split("-"))
        
        content = f"""---
name: {name}
description: {desc or "No description provided."}
---

# {title} Playbook

Provide detailed instructions, rules, and best practices for the {title} skill here.

## 1. Core Principles
* Principle 1
* Principle 2

## 2. Operational CLI Commands
```bash
# Provide exact command lines
./helper.sh command-here
```

## 3. Implementation Checklist & Verification
* [ ] Task 1
* [ ] Verify task 1
"""
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Create optional subdirectories
        for sub in ["scripts", "examples", "resources"]:
            os.makedirs(os.path.join(dest_dir, sub), exist_ok=True)
            
        # Write scripts/README.md
        with open(os.path.join(dest_dir, "scripts", "README.md"), 'w', encoding='utf-8') as f:
            f.write("# Custom Scripts\n\nPlace helper scripts for this skill in this directory.\n")
            
        # Write examples/README.md
        with open(os.path.join(dest_dir, "examples", "README.md"), 'w', encoding='utf-8') as f:
            f.write("# Reference Examples\n\nInclude reference implementations and usage examples here.\n")
            
        # Write resources/README.md
        with open(os.path.join(dest_dir, "resources", "README.md"), 'w', encoding='utf-8') as f:
            f.write("# Resources & Templates\n\nPlace static assets, configurations, and templates here.\n")
            
        # Write validate.py (validation hook template)
        validate_py_content = """#!/usr/bin/env python3
import sys

def main() -> int:
    # Custom skill compliance validation check
    # Return 0 for pass, non-zero for failure
    print("Running compliance checks for this skill...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
        with open(os.path.join(dest_dir, "validate.py"), 'w', encoding='utf-8') as f:
            f.write(validate_py_content)
        try:
            os.chmod(os.path.join(dest_dir, "validate.py"), 0o755)
        except Exception:
            pass
            
        # Write setup.sh (setup script template)
        setup_sh_content = """#!/usr/bin/env bash
set -euo pipefail
# Custom skill setup or dependencies installation
echo "Setting up dependencies for this skill..."
"""
        with open(os.path.join(dest_dir, "setup.sh"), 'w', encoding='utf-8') as f:
            f.write(setup_sh_content)
        try:
            os.chmod(os.path.join(dest_dir, "setup.sh"), 0o755)
        except Exception:
            pass
            
        print_ok(f"Scaffolded skill '{name}' at '{dest_dir}' successfully.")
        run_sync()
    except Exception as e:
        print_err(f"Failed to create skill '{name}': {e}")
        sys.exit(1)

def handle_uninstall(name: str) -> None:
    if not name:
        print_err("Usage: helper.py skill uninstall <skill_name>")
        sys.exit(1)
        
    if not validation.validate_safe_identifier(name):
        print_err(f"Invalid skill name '{name}'. Only safe characters are allowed.")
        sys.exit(1)
        
    dest_p = os.path.join(SKILLS_DIR, name)
    if not os.path.exists(dest_p):
        print_err(f"Skill '{name}' is not installed.")
        sys.exit(1)
        
    try:
        shutil.rmtree(dest_p)
        print_ok(f"Successfully uninstalled skill '{name}'.")
        run_sync()
    except Exception as e:
        print_err(f"Failed to delete skill directory: {e}")
        sys.exit(1)

def run(args: List[str]) -> None:
    if not args:
        print("Usage: helper.py skill <list|install|uninstall|create> [args...]")
        sys.exit(1)
        
    subcmd = args[0].lower()
    if subcmd == "list":
        handle_list()
    elif subcmd == "install":
        source = args[1] if len(args) > 1 else ""
        handle_install(source)
    elif subcmd == "uninstall":
        name = args[1] if len(args) > 1 else ""
        handle_uninstall(name)
    elif subcmd == "create":
        name = args[1] if len(args) > 1 else ""
        desc = args[2] if len(args) > 2 else ""
        handle_create(name, desc)
    else:
        print_err(f"Unknown subcommand '{subcmd}'. Available: list, install, uninstall, create")
        sys.exit(1)
