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
CYAN = "\033[96m"
BOLD = "\033[1m"
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

def get_global_app_dir() -> str:
    home = os.path.expanduser("~")
    return os.path.join(home, ".gemini", "antigravity-cli")

def get_builtin_skills_dir() -> str:
    return os.path.join(get_global_app_dir(), "builtin", "skills")

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
        
        clone_success = False
        try:
            res = subprocess.run(['git', 'clone', '--depth', '1', source, temp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                clone_success = True
            else:
                print(f"[WARN] Git clone failed: {res.stderr.decode('utf-8', errors='ignore').strip()}")
        except Exception as e:
            print(f"[WARN] Git clone crashed: {e}")
            
        if clone_success:
            try:
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
            # Fallback: try builtin registry
            name = os.path.basename(source.rstrip("/").split("/")[-1])
            if name.endswith(".git"):
                name = name[:-4]
                
            print(f"[INFO] Attempting offline fallback for skill '{name}'...")
            builtin_p = os.path.join(get_builtin_skills_dir(), name)
            
            src_p = None
            if os.path.exists(builtin_p):
                src_p = builtin_p
                loc_type = "builtin"
                
            if src_p:
                dest_p = os.path.join(SKILLS_DIR, name)
                if os.path.exists(dest_p):
                    shutil.rmtree(dest_p)
                shutil.copytree(src_p, dest_p)
                print_ok(f"Installed skill '{name}' from offline {loc_type} fallback.")
            else:
                print_err(f"Failed to resolve skill '{name}'. Git clone failed and no builtin registry was found.")
                sys.exit(1)
    else:
        # Check if local path exists
        source_path = os.path.abspath(source)
        if os.path.exists(source_path):
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
        else:
            # Check if simple name exists in builtin registry
            name = source
            print(f"[INFO] Resolving local skill '{name}' from registry...")
            builtin_p = os.path.join(get_builtin_skills_dir(), name)
            
            src_p = None
            if os.path.exists(builtin_p):
                src_p = builtin_p
                loc_type = "builtin"
                
            if src_p:
                dest_p = os.path.join(SKILLS_DIR, name)
                if os.path.exists(dest_p):
                    shutil.rmtree(dest_p)
                shutil.copytree(src_p, dest_p)
                print_ok(f"Installed skill '{name}' from local {loc_type} registry.")
            else:
                print_err(f"Skill '{name}' could not be resolved as local path, git URL, or builtin registry.")
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

def handle_test(name: str) -> None:
    if not name:
        print_err("Usage: helper.py skill test <skill_name>")
        sys.exit(1)
        
    if not validation.validate_safe_identifier(name):
        print_err(f"Invalid skill name '{name}'. Only safe characters are allowed.")
        sys.exit(1)
        
    skill_dir = os.path.join(SKILLS_DIR, name)
    if not os.path.exists(skill_dir):
        print_err(f"Skill '{name}' is not installed at '{skill_dir}'.")
        sys.exit(1)
        
    print(f"\n{CYAN}{BOLD}=========================================================={RESET}")
    print(f"   Testing Active Skill Compliance: {name}")
    print(f"{CYAN}{BOLD}=========================================================={RESET}\n")
    
    # 1. Verify SKILL.md
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        print_err("Metadata check: FAIL (SKILL.md not found)")
        sys.exit(1)
    else:
        print_ok("Metadata check: SKILL.md exists")
        
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        content_norm = content.replace('\r\n', '\n')
        m_fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', content_norm, re.DOTALL)
        if not m_fm:
            print_err("Metadata check: FAIL (Invalid frontmatter format)")
        else:
            fm_text = m_fm.group(1)
            name_val = re.search(r'name:\s*(.*?)(?:\n|$)', fm_text)
            desc_val = re.search(r'description:\s*(.*?)(?:\n|$)', fm_text)
            
            if not name_val or not desc_val:
                print_err("Metadata check: FAIL (Missing 'name' or 'description' in frontmatter)")
            else:
                print_ok(f"Metadata check: Valid frontmatter (Name: {name_val.group(1).strip()}, Desc: {desc_val.group(1).strip()})")
    except Exception as e:
        print_err(f"Metadata check: FAIL (Error reading SKILL.md: {e})")
        
    # 2. Check subdirectory structures
    dirs = ["scripts", "examples", "resources"]
    for d in dirs:
        d_path = os.path.join(skill_dir, d)
        if os.path.isdir(d_path):
            print_ok(f"Directory structure: '{d}/' directory present")
        else:
            print(f"{YELLOW}[INFO] Directory structure: '{d}/' directory not present (optional){RESET}")
            
    # 3. Check and execute validation hook
    hook_py = os.path.join(skill_dir, "validate.py")
    hook_sh = os.path.join(skill_dir, "setup.sh")
    
    hook_path = None
    if os.path.exists(hook_py):
        hook_path = hook_py
    elif os.path.exists(hook_sh):
        hook_path = hook_sh
        
    if hook_path:
        print(f"Executing validation hook: {os.path.basename(hook_path)}...")
        try:
            if hook_path.endswith(".py"):
                res = subprocess.run([sys.executable, hook_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                res = subprocess.run(["bash", hook_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
            if res.returncode == 0:
                print_ok(f"Validation hook: PASS (Exit code 0)")
                if res.stdout.strip():
                    print(f"Stdout:\n{res.stdout.strip()}")
            else:
                print_err(f"Validation hook: FAIL (Exit code {res.returncode})")
                if res.stdout.strip():
                    print(f"Stdout:\n{res.stdout.strip()}", file=sys.stderr)
                if res.stderr.strip():
                    print(f"Stderr:\n{res.stderr.strip()}", file=sys.stderr)
        except Exception as e:
            print_err(f"Validation hook: CRASH (Error executing hook: {e})")
    else:
        print(f"{YELLOW}[INFO] Validation hook: SKIPPED (No validate.py or setup.sh hook found){RESET}")
        
    print(f"\n{CYAN}{BOLD}=========================================================={RESET}")
    print(f"   Skill '{name}' testing completed.")
    print(f"{CYAN}{BOLD}=========================================================={RESET}\n")

def run(args: List[str]) -> None:
    if not args:
        print("Usage: helper.py skill <list|install|uninstall|create|test> [args...]")
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
    elif subcmd == "test":
        name = args[1] if len(args) > 1 else ""
        handle_test(name)
    else:
        print_err(f"Unknown subcommand '{subcmd}'. Available: list, install, uninstall, create, test")
        sys.exit(1)
