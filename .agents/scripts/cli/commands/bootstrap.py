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
    helpers = ["helper.sh", "helper.ps1", ".agents/git_profiles.example"]
    for h in helpers:
        src_file = os.path.join(src_root, h)
        dest_file = os.path.join(target_root, h)
        if os.path.exists(src_file) and not os.path.exists(dest_file):
            try:
                shutil.copy2(src_file, dest_file)
                if h.endswith(".sh"):
                    os.chmod(dest_file, 0o755)
            except Exception:
                pass

    # Initialize clean memory folder
    target_mem = os.path.join(target_root, ".agents/memory")
    os.makedirs(os.path.join(target_mem, "decisions"), exist_ok=True)
    
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
    AAC_VERSION = "2.3.0"
    if not os.path.exists(agents_file):
        template = f"""# AGENTS.md — {name}

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand — see the context map below.

## 1. What this project is
- **Product:** {name}
- **Version:** {AAC_VERSION}
- **Stack:** {stack.capitalize()} ({arch.upper()})
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
*(Listed first and emphasized — the model weights early, ALWAYS/NEVER-style rules more reliably than buried prose.)*

- **NEVER** commit secrets, `.env*` files, or credentials. Use the secrets approach documented in `.agents/memory/architecture.md`.
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work, and update it when status changes.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first — supersede an old one, don't duplicate it.
- **ALWAYS** use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`) with the task ID in the body.
- **NEVER** run or write raw CLI scripts directly in the workspace root; keep them organized in target directories.
- **ALWAYS** register any new custom skills in their respective subdirectory with a `SKILL.md`.
- **ALWAYS** acquire locks on modules before beginning edits to avoid conflicting parallel modifications.
- **ALWAYS** run `.agents/scripts/validate.py` locally and verify it passes before proposing commits or pull requests.
- **ALWAYS** align your git branch name with an active issue ID and verify a matching issue file exists under `.agents/issues/` (e.g. branch `feat/issue-12` aligns with `.agents/issues/issue_12.md`).
- **ALWAYS** strictly conform to the schemas defined in `.agents/schema.md` when modifying database models or API contracts.
- **NEVER** write to or rely on global configurations outside the project directory (e.g., in user home directory). Everything must be stored strictly within the workspace level under `.agents/` and tracked in git to ensure multi-developer environment consistency.
- **ALWAYS** copy `.agents/git_profiles.example` to `.agents/git_profiles.json` during environment initialization to set up local identity rotation, and verify the `.json` file is never staged or committed.

## 3. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, non-negotiables, map | Always — every prompt |
| `.agents/skills/adr-writer/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/debugging/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/security-audit/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/tasking/SKILL.md` | Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/world-class-programmer/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand, referenced from architecture.md and the `adr-writer` skill — never auto-loaded |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.md` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |

If you're about to paste a paragraph of explanation into this file, it almost certainly belongs in a skill or memory file instead, pulled in with `@path` only when needed. That's what keeps the per-prompt token cost flat as the project grows.

## 4. Working protocol
1. **Fresh Workspace Initialization:** If starting in a completely empty project directory, the agent MUST immediately execute `./helper.sh bootstrap` to interactively setup the project name, stack (Python, Node, PHP), architecture blueprint (`schema.md`), and task board before writing any code.
2. **Before coding:** read `.agents/tasks/board.md`, claim the task, move it to `Doing`.
3. **Pre-Implementation:** Perform a Pre-Implementation Impact Analysis comparing at least two options (following the `world-class-programmer` playbook) to evaluate long-term maintenance and UI/UX simplicity.
4. **Before any architecture-affecting change:** pull `@.agents/memory/architecture.md` and check `.agents/memory/decisions/` for a relevant ADR.
5. **While working:** prefer invoking an existing skill over re-deriving a workflow from scratch.
6. **Before marking a task `Completed`:** tests pass, board updated with implementation notes, and — if the change was architecturally significant — a new or superseding ADR exists (`adr-writer` skill).
7. **End of session:** run `/sync-memory` to fold session learnings into memory and prune anything stale (see `.agents/workflows/sync-memory.md`).

## 5. Git & review
- Branches: `feat/<task-id>-slug`, `fix/<task-id>-slug`.
- One task = one PR where practical; link the task ID in the PR description.
- No self-merging architecturally significant PRs — a second reviewer (human or the `code-review` skill) signs off first.

## 6. Tool permissions
Default to `request-review` in `agy config` for this repo (pauses before destructive/file-write actions). Reserve `proceed-in-sandbox` for disposable environments only. Never set `always-proceed` on a repo with reachable production credentials.

## 7. Maintaining this file
Reviewed like code. Budget: stay under ~150 lines. If it grows past that, move the newest, least-universal addition into a skill or memory file and leave a one-line pointer here instead.
"""
        with open(agents_file, 'w', encoding='utf-8') as f:
            f.write(template)
        print("Created AGENTS.md from V2 template.")
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

