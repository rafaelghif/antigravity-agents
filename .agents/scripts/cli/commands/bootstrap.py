import sys
import os
import re
import json

def create_clean_architecture(root):
    dirs = [
        "src/core/entities",
        "src/core/usecases",
        "src/infrastructure/database",
        "src/infrastructure/repositories",
        "src/presentation/api",
        "src/presentation/cli",
        "tests/unit",
        "tests/integration"
    ]
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)
        # Create empty __init__.py
        with open(os.path.join(root, d, "__init__.py"), 'w') as f:
            f.write("")

def create_layered_architecture(root):
    dirs = [
        "src/api",
        "src/services",
        "src/repositories",
        "src/models",
        "tests"
    ]
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)
        with open(os.path.join(root, d, "__init__.py"), 'w') as f:
            f.write("")

def create_mvc_architecture(root):
    dirs = [
        "src/models",
        "src/views",
        "src/controllers",
        "tests"
    ]
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)
        with open(os.path.join(root, d, "__init__.py"), 'w') as f:
            f.write("")

def copy_core_files():
    """Copy all core agent files and skills from the running installation source
    to the target project workspace if they are missing."""
    import shutil
    
    # Locate the running script's project root (where .agents directory is located)
    # Since this command runs from .agents/scripts/cli/commands/bootstrap.py
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    target_root = os.path.abspath(".")
    
    # If target is the same as source, nothing to copy
    if src_root == target_root:
        return
        
    print("Copying core agent scripts, skills, and CLI helper tools...")
    
    # Directories to copy recursively
    core_dirs = [
        ".agents/scripts",
        ".agents/skills",
        ".agents/workflows",
    ]
    
    for d in core_dirs:
        src_dir = os.path.join(src_root, d)
        target_dir = os.path.join(target_root, d)
        if os.path.exists(src_dir):
            if os.path.exists(target_dir):
                # Copy individual files that are missing
                for root, _, files in os.walk(src_dir):
                    rel_path = os.path.relpath(root, src_dir)
                    dest_folder = os.path.join(target_dir, rel_path)
                    os.makedirs(dest_folder, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_folder, file)
                        if not os.path.exists(dest_file):
                            try:
                                shutil.copy2(src_file, dest_file)
                            except Exception:
                                pass
            else:
                try:
                    shutil.copytree(src_dir, target_dir)
                except Exception:
                    pass
                
    # Root helper wrappers
    helpers = ["helper.sh", "helper.ps1", ".agents/git_profiles.example", ".agents/rules.md"]
    for h in helpers:
        src_file = os.path.join(src_root, h)
        dest_file = os.path.join(target_root, h)
        if os.path.exists(src_file) and not os.path.exists(dest_file):
            try:
                # Ensure parent dir exists
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(src_file, dest_file)
                if h.endswith(".sh"):
                    os.chmod(dest_file, 0o755)
            except Exception:
                pass

    # Initialize clean memory, tasks, and issues folders
    target_mem = os.path.join(target_root, ".agents/memory")
    os.makedirs(os.path.join(target_mem, "decisions"), exist_ok=True)
    os.makedirs(os.path.join(target_root, ".agents/tasks"), exist_ok=True)
    os.makedirs(os.path.join(target_root, ".agents/issues"), exist_ok=True)
    
    # Copy template memory files
    src_templates = os.path.join(src_root, ".agents/memory/templates")
    if os.path.exists(src_templates):
        for file in os.listdir(src_templates):
            if file.endswith(".template"):
                src_file = os.path.join(src_templates, file)
                dest_file = os.path.join(target_mem, file[:-9])  # remove .template suffix
                if not os.path.exists(dest_file):
                    try:
                        shutil.copy2(src_file, dest_file)
                    except Exception:
                        pass

def run(args):
    print("==========================================================")
    print("   Antigravity V2 Project Bootstrapper                    ")
    print("==========================================================")
    
    # Prompt for project details
    # To keep it friendly for automation, we support command-line arguments:
    # helper.py bootstrap <name> <stack> <architecture> [options]
    if len(args) < 3:
        print("Interactive Setup (or run: helper.sh bootstrap <name> <stack: python|node|php> <arch: clean|layered|mvc>)")
        name = input("Project Name: ").strip()
        stack = input("Programming Stack (python/node/php): ").strip().lower()
        arch = input("Architecture Pattern (clean/layered/mvc): ").strip().lower()
    else:
        name = args[0]
        stack = args[1].lower()
        arch = args[2].lower()

    if not name or stack not in ("python", "node", "php") or arch not in ("clean", "layered", "mvc"):
        print("Error: Invalid inputs. Stack must be 'python', 'node', or 'php'. Architecture must be 'clean', 'layered', or 'mvc'.")
        sys.exit(1)

    print(f"\nInitializing '{name}' using '{stack}' with '{arch}' architecture...")

    # 1. Generate Folder Structure
    if arch == "clean":
        create_clean_architecture(".")
    elif arch == "layered":
        create_layered_architecture(".")
    elif arch == "mvc":
        create_mvc_architecture(".")

    # Ensure .agents and subdirectories exist
    os.makedirs(".agents", exist_ok=True)
    os.makedirs(".agents/tasks", exist_ok=True)
    os.makedirs(".agents/issues", exist_ok=True)

    copy_core_files()

    # 2. Write Base Configuration Files
    if stack == "python":
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write("# Project dependencies\npytest\nflake8\n")
    elif stack == "node":
        with open("package.json", 'w', encoding='utf-8') as f:
            f.write(f'{{\n  "name": "{name.lower()}",\n  "version": "1.0.0",\n  "scripts": {{\n    "test": "jest",\n    "lint": "eslint ."\n  }}\n}}')
    elif stack == "php":
        with open("composer.json", 'w', encoding='utf-8') as f:
            f.write(f'{{\n  "name": "dev/{name.lower()}",\n  "require": {{}},\n  "require-dev": {{\n    "phpunit/phpunit": "^9.0"\n  }}\n}}')

    # 3. Create .gitignore
    if not os.path.exists(".gitignore"):
        with open(".gitignore", 'w', encoding='utf-8') as f:
            f.write(".env\n__pycache__/\nnode_modules/\nvendor/\n.pytest_cache/\n.agents/locks.json\n")

    # 4. Generate .agents/schema.md
    schema_content = f"""# Project Architecture Blueprint: {name}

## 1. Stack Details
- **Language/Platform**: {stack.capitalize()}
- **Pattern**: {arch.upper()} Architecture

## 2. Directory Layout
- `src/`: Core codebase.
- `tests/`: Unit and integration testing suite.

## 3. Structural Rules
- Modules must communicate only through defined APIs.
- Domain entities must have zero external dependencies.
"""
    with open(".agents/schema.md", 'w', encoding='utf-8') as f:
        f.write(schema_content)
    print("Generated '.agents/schema.md' architecture blueprint.")

    # 5. Update or Create AGENTS.md
    agents_file = "AGENTS.md"
    AAC_VERSION = "2.16.0"
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    src_agents = os.path.join(src_root, "AGENTS.md")
    
    if not os.path.exists(agents_file):
        if os.path.exists(src_agents):
            try:
                with open(src_agents, 'r', encoding='utf-8') as f:
                    template = f.read()
                # Personalize template
                template = re.sub(r'# AGENTS.md — .*', f'# AGENTS.md — {name}', template)
                template = re.sub(r'-\s+\*\*Product:\*\*.*', f'- **Product:** {name}', template)
                template = re.sub(r'-\s+\*\*Stack:\*\*.*', f'- **Stack:** {stack.capitalize()} ({arch.upper()})', template)
                template = re.sub(r'-\s+\*\*Version:\*\*.*', f'- **Version:** {AAC_VERSION}', template)
                with open(agents_file, 'w', encoding='utf-8') as f:
                    f.write(template)
                print("Created AGENTS.md from source repository template.")
            except Exception as e:
                print(f"Warning: Could not create AGENTS.md from source template: {e}")
        else:
            # Fallback to minimal header if source doesn't exist
            fallback = f"# AGENTS.md — {name}\n\n- **Product:** {name}\n- **Version:** {AAC_VERSION}\n- **Stack:** {stack.capitalize()} ({arch.upper()})\n"
            with open(agents_file, 'w', encoding='utf-8') as f:
                f.write(fallback)
            print("Created fallback minimal AGENTS.md.")
    else:
        with open(agents_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'-\s+\*\*Stack:\*\*.*', f'- **Stack:** {stack.capitalize()} ({arch.upper()})', content)
        content = re.sub(r'-\s+\*\*Product:\*\*.*', f'- **Product:** {name}', content)
        if re.search(r'-\s+\*\*Version:\*\*.*', content):
            content = re.sub(r'-\s+\*\*Version:\*\*.*', f'- **Version:** {AAC_VERSION}', content)
        else:
            # Insert after the Product line
            content = re.sub(r'(-\s+\*\*Product:\*\*.*)', r'\1\n- **Version:** ' + AAC_VERSION, content)
        with open(agents_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated AGENTS.md with new stack, product, and version.")

    # 6. Update .agents/rules.md
    rules_file = ".agents/rules.md"
    if os.path.exists(rules_file):
        test_cmds = {"python": "pytest", "node": "npm run test", "php": "./vendor/bin/phpunit"}
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        rules_content = re.sub(r'Use \*\*.*?\*\* for the main product stack\.', f'Use **{stack.capitalize()}** for the main product stack.', rules_content)
        rules_content = re.sub(r'test command is: `.*?`\.', f'test command is: `{test_cmds[stack]}`.', rules_content)
        with open(rules_file, 'w', encoding='utf-8') as f:
            f.write(rules_content)
        print("Updated '.agents/rules.md' style and test command configuration.")

    # 7. Initialize Task Board
    board_file = ".agents/tasks/board.md"
    with open(board_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Task Board: {name}

This board tracks active development tasks.

## Todo
- [ ] Implement initial model/entity definitions <!-- id: task-bootstrap -->

## Doing

## Done
""")
    print("Initialized task board at '.agents/tasks/board.md'.")
    print("\nProject bootstrapping completed successfully! Run './helper.sh validate' to verify.")

    # 8. Git Profile Onboarding Wizard
    profiles_file = ".agents/git_profiles.json"
    if not os.path.exists(profiles_file):
        example_file = ".agents/git_profiles.example"
        if os.path.exists(example_file):
            import shutil
            try:
                shutil.copy2(example_file, profiles_file)
            except Exception:
                pass
            
    has_profiles = False
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                p_data = json.load(f)
            if p_data.get("profiles"):
                has_profiles = True
        except Exception:
            pass
            
    if not has_profiles:
        print("\n==========================================================")
        print("   Onboarding: Git Developer Profile Configuration       ")
        print("==========================================================")
        print("No Git profiles configured in '.agents/git_profiles.json'.")
        is_interactive = sys.stdin.isatty()
        if is_interactive:
            try:
                setup_now = input("Would you like to configure your local developer profile now? (y/n): ").strip().lower()
                if setup_now == 'y':
                    prof_name = input("Profile Name (e.g. corp, personal): ").strip()
                    prof_email = input("Git config Email: ").strip()
                    if prof_name and prof_email:
                        new_profile = {
                            "name": prof_name,
                            "email": prof_email,
                            "active": True
                        }
                        with open(profiles_file, 'w', encoding='utf-8') as f:
                            json.dump({"profiles": [new_profile]}, f, indent=2)
                        
                        import subprocess
                        subprocess.run(['git', 'config', 'user.name', prof_name])
                        subprocess.run(['git', 'config', 'user.email', prof_email])
                        print(f"[OK] Created active profile '{prof_name}' and updated local Git config.")
            except Exception as e:
                print(f"Skipping profile wizard: {e}")
        else:
            print("Note: To set up your credentials rotation, configure '.agents/git_profiles.json'")
            print("or run: ./helper.sh profile add <name> <email>")
        print("==========================================================")

