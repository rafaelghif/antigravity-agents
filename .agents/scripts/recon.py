import os
import re
import sys

def scan_workspace():
    detected_stack = []
    build_tool = None
    test_command = "N/A"
    lint_command = "N/A"
    build_command = "N/A"
    
    has_py = False
    has_js = False
    has_go = False
    has_rs = False
    has_java = False
    has_docker = False
    has_prisma = False
    
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', '.pytest_cache'}
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file == 'package.json':
                has_js = True
            elif file.endswith('.py'):
                has_py = True
            elif file == 'go.mod':
                has_go = True
            elif file == 'Cargo.toml':
                has_rs = True
            elif file in ('pom.xml', 'build.gradle', 'build.gradle.kts'):
                has_java = True
            elif file in ('Dockerfile', 'docker-compose.yml'):
                has_docker = True
            elif 'prisma' in file.lower() or 'schema.prisma' in file:
                has_prisma = True
                
    if has_js:
        detected_stack.append("JavaScript/TypeScript (Node.js)")
        build_tool = "npm"
        test_command = "npm run test"
        lint_command = "npm run lint"
        build_command = "npm run build"
    if has_py:
        detected_stack.append("Python 3")
        if test_command == "N/A":
            test_command = "pytest"
            lint_command = "flake8 ."
            build_command = "pip install -r requirements.txt"
    if has_go:
        detected_stack.append("Go (Golang)")
        test_command = "go test ./..."
        lint_command = "golangci-lint run"
        build_command = "go build"
    if has_rs:
        detected_stack.append("Rust")
        test_command = "cargo test"
        lint_command = "cargo clippy"
        build_command = "cargo build"
    if has_java:
        detected_stack.append("Java/Kotlin")
        test_command = "mvn test"
        build_command = "mvn clean package"
    if has_docker:
        detected_stack.append("Docker")
    if has_prisma:
        detected_stack.append("Prisma ORM")

    # Defaults if nothing is found
    if not detected_stack:
        detected_stack.append("General Project")
        
    return {
        "stack": ", ".join(detected_stack),
        "build_tool": build_tool,
        "test_command": test_command,
        "lint_command": lint_command,
        "build_command": build_command
    }

def update_agents_md(scan_results):
    agents_file = 'AGENTS.md'
    if not os.path.exists(agents_file):
        print(f"Warning: {agents_file} not found.")
        return

    with open(agents_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Stack placeholder
    stack_pattern = r'(-\s+\*\*Stack:\*\*)\s+.*'
    replacement = f'\\1 {scan_results["stack"]}'
    new_content = re.sub(stack_pattern, replacement, content)

    with open(agents_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated AGENTS.md with detected stack.")

def update_rules_md(scan_results):
    rules_file = '.agents/rules.md'
    if not os.path.exists(rules_file):
        print(f"Warning: {rules_file} not found.")
        return

    with open(rules_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace commands in rules
    content = re.sub(r'Use \*\*.*?\*\* (?:for the main product stack|for all CLI scripting)\.?', f'Use **{scan_results["stack"]}** for the main product stack.', content)
    content = re.sub(r'test command is: `.*?`\.|test command before.*', f'test command is: `{scan_results["test_command"]}`.', content)
    
    with open(rules_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated .agents/rules.md with build and test guidelines.")

if __name__ == '__main__':
    print("Running enterprise auto-reconnaissance scan...")
    results = scan_workspace()
    print(f"Detected Stack: {results['stack']}")
    print(f"Recommended Test: {results['test_command']}")
    
    update_agents_md(results)
    update_rules_md(results)
    print("Auto-reconnaissance completed successfully!")
