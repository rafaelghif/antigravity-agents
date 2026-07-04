import sys
import os
import re
import json

def detect_project_stack(root=".") -> str:
    """Detect the programming stack from the files present in the root directory."""
    if os.path.exists(os.path.join(root, "go.mod")):
        return "go"
    if os.path.exists(os.path.join(root, "Cargo.toml")):
        return "rust"
    if os.path.exists(os.path.join(root, "package.json")):
        return "node"
    if os.path.exists(os.path.join(root, "composer.json")):
        return "php"
    if (os.path.exists(os.path.join(root, "requirements.txt")) or 
            os.path.exists(os.path.join(root, "Pipfile")) or 
            os.path.exists(os.path.join(root, "pyproject.toml"))):
        return "python"
    
    # Check for Java
    if os.path.exists(os.path.join(root, "pom.xml")) or os.path.exists(os.path.join(root, "build.gradle")):
        return "java"
    
    # Check for C#
    if os.path.exists(root) and os.path.isdir(root):
        try:
            for f in os.listdir(root):
                if f.endswith(".csproj") or f.endswith(".sln"):
                    return "csharp"
        except Exception:
            pass
            
    return ""

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

def read_template(src_root, filename, fallbacks=None):
    """Read a configuration template from the source directory, falling back if missing."""
    template_path = os.path.join(src_root, ".agents/templates", filename)
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            pass
    if fallbacks is not None:
        return fallbacks
    return ""

def copy_core_files():
    """Copy all core agent files and skills from the running installation source
    to the target project workspace if they are missing."""
    import shutil
    
    # Locate the running script's project root (where .agents directory is located)
    # Since this command runs from .agents/scripts/cli/commands/bootstrap.py
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    target_root = os.path.abspath(".")
    
    # If target is the same as source, nothing to copy
    if src_root == target_root:
        return
        
    print("Copying core agent scripts, skills, and CLI helper tools...")
    
    def is_ignored(full_path):
        # Resolve path relative to src_root
        try:
            rel = os.path.relpath(full_path, src_root)
        except ValueError:
            p1 = os.path.splitdrive(os.path.abspath(full_path))[1]
            p2 = os.path.splitdrive(os.path.abspath(src_root))[1]
            rel = os.path.relpath(p1, p2)
        parts = rel.replace('\\', '/').split('/')
        exclude_parts = {'__pycache__', '.git', '.pytest_cache', '.next', '.nuxt', 'node_modules', 'vendor'}
        if any(p in exclude_parts for p in parts):
            return True
        base = os.path.basename(rel)
        exclude_files = {'git_profiles.json', 'locks.json', '.DS_Store', 'Thumbs.db'}
        if base in exclude_files:
            return True
        if base.endswith(('.pyc', '.pyo')):
            return True
        return False

    # Directories to copy recursively
    core_dirs = [
        ".agents/scripts",
        ".agents/skills",
        ".agents/workflows",
        ".agents/templates",
    ]
    
    for d in core_dirs:
        src_dir = os.path.join(src_root, d)
        target_dir = os.path.join(target_root, d)
        if os.path.exists(src_dir):
            if os.path.exists(target_dir):
                # Copy individual files that are missing
                for root, dirs, files in os.walk(src_dir):
                    dirs[:] = [d_name for d_name in dirs if not is_ignored(os.path.join(root, d_name))]
                    try:
                        rel_path = os.path.relpath(root, src_dir)
                    except ValueError:
                        p1 = os.path.splitdrive(os.path.abspath(root))[1]
                        p2 = os.path.splitdrive(os.path.abspath(src_dir))[1]
                        rel_path = os.path.relpath(p1, p2)
                    dest_folder = os.path.join(target_dir, rel_path)
                    os.makedirs(dest_folder, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(root, file)
                        if is_ignored(src_file):
                            continue
                        dest_file = os.path.join(dest_folder, file)
                        if not os.path.exists(dest_file):
                            try:
                                shutil.copy2(src_file, dest_file)
                            except Exception:
                                pass
            else:
                try:
                    def copytree_ignore(path, names):
                        ignored = []
                        for name in names:
                            if is_ignored(os.path.join(path, name)):
                                ignored.append(name)
                        return ignored
                    shutil.copytree(src_dir, target_dir, ignore=copytree_ignore)
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
    os.makedirs(os.path.join(target_mem, "blueprints"), exist_ok=True)
    os.makedirs(os.path.join(target_root, ".agents/tasks"), exist_ok=True)
    os.makedirs(os.path.join(target_root, ".agents/issues"), exist_ok=True)
    
    # Copy blueprints
    src_blueprints = os.path.join(src_root, ".agents/memory/blueprints")
    if os.path.exists(src_blueprints):
        target_blueprints = os.path.join(target_mem, "blueprints")
        for file in os.listdir(src_blueprints):
            src_file = os.path.join(src_blueprints, file)
            dest_file = os.path.join(target_blueprints, file)
            if os.path.isfile(src_file) and not os.path.exists(dest_file):
                try:
                    shutil.copy2(src_file, dest_file)
                except Exception:
                    pass

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

    # Copy projects.example to projects.json if it doesn't exist
    src_projects_ex = os.path.join(src_root, ".agents/projects.example")
    dest_projects_json = os.path.join(target_root, ".agents/projects.json")
    if os.path.exists(src_projects_ex) and not os.path.exists(dest_projects_json):
        try:
            shutil.copy2(src_projects_ex, dest_projects_json)
        except Exception:
            pass

def run(args):
    print("==========================================================")
    print("   Antigravity V2 Project Bootstrapper                    ")
    print("==========================================================")
    
    # Auto-detect stack
    detected_stack = detect_project_stack(".")
    
    # Prompt for project details
    # To keep it friendly for automation, we support command-line arguments:
    # helper.py bootstrap <name> <stack> <architecture> [options]
    if len(args) < 3:
        print("Interactive Setup (or run: helper.sh bootstrap <name> <stack> <arch: clean|layered|mvc>)")
        default_name = os.path.basename(os.path.abspath(".")).strip()
        name = input(f"Project Name (default: {default_name}): ").strip()
        if not name:
            name = default_name
            
        stack_prompt = "Programming Stack"
        if detected_stack:
            stack_prompt += f" (Auto-detected: '{detected_stack}', press enter to accept): "
        else:
            stack_prompt += " (python/node/php/go/rust/etc.): "
        stack = input(stack_prompt).strip().lower()
        if not stack and detected_stack:
            stack = detected_stack
            
        arch = input("Architecture Pattern (clean/layered/mvc): ").strip().lower()
    else:
        name = args[0]
        stack = args[1].lower()
        arch = args[2].lower()

    if not name or not stack or arch not in ("clean", "layered", "mvc"):
        print("Error: Invalid inputs. Stack cannot be empty. Architecture must be 'clean', 'layered', or 'mvc'.")
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
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    
    if stack == "python":
        req_content = read_template(src_root, "python_requirements.txt.template", "# Project dependencies\npytest\nflake8\n")
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write(req_content)
    elif stack == "node":
        pkg_content = read_template(src_root, "node_package.json.template", '{\n  "name": "{{NAME}}",\n  "version": "1.0.0",\n  "scripts": {\n    "test": "jest",\n    "lint": "eslint ."\n  }\n}')
        pkg_content = pkg_content.replace("{{NAME}}", name.lower())
        with open("package.json", 'w', encoding='utf-8') as f:
            f.write(pkg_content)
    elif stack == "php":
        comp_content = read_template(src_root, "php_composer.json.template", '{\n  "name": "dev/{{NAME}}",\n  "require": {},\n  "require-dev": {\n    "phpunit/phpunit": "^9.0"\n  }\n}')
        comp_content = comp_content.replace("{{NAME}}", name.lower())
        with open("composer.json", 'w', encoding='utf-8') as f:
            f.write(comp_content)

    # 3. Create .gitignore and .antigravityignore
    if not os.path.exists(".gitignore"):
        git_ignore_content = read_template(src_root, "gitignore.template", ".env\n__pycache__/\nnode_modules/\nvendor/\n.pytest_cache/\n.agents/locks.json\n")
        with open(".gitignore", 'w', encoding='utf-8') as f:
            f.write(git_ignore_content)
            
    if not os.path.exists(".antigravityignore"):
        anti_ignore_content = read_template(src_root, "antigravityignore.template", "")
        if anti_ignore_content:
            with open(".antigravityignore", 'w', encoding='utf-8') as f:
                f.write(anti_ignore_content)

    # 3.1 Create GitHub CI workflow
    github_workflow_dir = ".github/workflows"
    github_workflow_file = os.path.join(github_workflow_dir, "verify.yml")
    if not os.path.exists(github_workflow_file):
        os.makedirs(github_workflow_dir, exist_ok=True)
        ci_content = read_template(src_root, "ci_github_workflow.yml.template", "")
        if ci_content:
            with open(github_workflow_file, 'w', encoding='utf-8') as f:
                f.write(ci_content)
            print("Generated '.github/workflows/verify.yml' CI pipeline configuration.")

    # 4. Generate .agents/schema.md
    schema_content = read_template(src_root, "schema.md.template", "# Project Architecture Blueprint: {{NAME}}\n\n## 1. Stack Details\n- **Language/Platform**: {{STACK}}\n- **Pattern**: {{ARCH}} Architecture\n")
    schema_content = schema_content.replace("{{NAME}}", name).replace("{{STACK}}", stack.capitalize()).replace("{{ARCH}}", arch.upper())
    with open(".agents/schema.md", 'w', encoding='utf-8') as f:
        f.write(schema_content)
    print("Generated '.agents/schema.md' architecture blueprint.")

    # 5. Update or Create AGENTS.md
    agents_file = "AGENTS.md"
    AAC_VERSION = "2.126.0"
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
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
        test_cmds = {
            "python": "pytest", 
            "node": "npm run test", 
            "php": "./vendor/bin/phpunit",
            "go": "go test ./...",
            "rust": "cargo test",
            "csharp": "dotnet test",
            "java": "gradle test"
        }
        test_cmd = test_cmds.get(stack, f"run {stack} tests")
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        rules_content = re.sub(r'Use \*\*.*?\*\* for the main product stack\.', f'Use **{stack.capitalize()}** for the main product stack.', rules_content)
        rules_content = re.sub(r'test command is: `.*?`\.', f'test command is: `{test_cmd}`.', rules_content)
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
        is_interactive = sys.stdin.isatty() and os.getenv("ANTIGRAVITY_AGENT") != "1" and os.getenv("ANTIGRAVITY_NONINTERACTIVE") != "1"
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

    # 9. Next Steps Configuration Guide
    print("\n==========================================================")
    print("   Next Steps: Workspace Configuration Guide             ")
    print("==========================================================")
    print("1. Git Identity Rotation (Avoid commits with wrong emails):")
    print("   Verify '.agents/git_profiles.json' exists. To add new profiles:")
    print("     ./helper.sh profile add <name> <email>")
    print("2. Monorepos & Multi-Project Validation:")
    print("   To run tests across multiple projects inside this repository,")
    print("   copy '.agents/projects.example' to '.agents/projects.json'")
    print("   and configure your project paths.")
    print("3. Claim a Task and Start Coding:")
    print("   Open '.agents/tasks/board.md' to see available issues.")
    print("   Checkout a task using: ./helper.sh issue checkout <task-id>")
    print("==========================================================")

