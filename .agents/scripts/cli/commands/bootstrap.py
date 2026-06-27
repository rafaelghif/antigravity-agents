import sys
import os
import re

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

    # 5. Update AGENTS.md
    agents_file = "AGENTS.md"
    if os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'-\s+\*\*Stack:\*\*.*', f'- **Stack:** {stack.capitalize()} ({arch.upper()})', content)
        content = re.sub(r'-\s+\*\*Product:\*\*.*', f'- **Product:** {name}', content)
        with open(agents_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated AGENTS.md with new stack and product name.")

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
