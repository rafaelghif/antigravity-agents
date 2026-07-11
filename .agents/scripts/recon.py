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
    has_php = False
    has_laravel = False
    has_tailwind = False
    has_css = False
    has_html = False
    has_dotnet = False
    has_dotnet_core = False
    has_dotnet_framework = False
    
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', '.pytest_cache', 'vendor', '.agents', '.lock', 'logs', 'dist', 'build', 'out'}
    
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
            elif file == 'composer.json' or file.endswith('.php'):
                has_php = True
                if file == 'artisan':
                    has_laravel = True
            elif 'tailwind.config' in file:
                has_tailwind = True
            elif file.endswith(('.css', '.scss', '.sass')):
                has_css = True
            elif file.endswith('.html'):
                has_html = True
            elif file.endswith('.csproj'):
                has_dotnet = True
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        csproj_content = f.read()
                    if '<TargetFrameworkVersion>v' in csproj_content:
                        has_dotnet_framework = True
                    elif '<TargetFramework>' in csproj_content or 'Sdk="Microsoft.NET.Sdk' in csproj_content:
                        has_dotnet_core = True
                except Exception:
                    pass
            elif file.endswith('.sln'):
                has_dotnet = True
                
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
    if has_php:
        if has_laravel:
            detected_stack.append("PHP (Laravel)")
            test_command = "php artisan test"
            build_command = "composer install && php artisan migrate"
        else:
            detected_stack.append("PHP")
            test_command = "./vendor/bin/phpunit"
            build_command = "composer install"
    if has_tailwind:
        detected_stack.append("Tailwind CSS")
    if has_css and not has_tailwind:
        detected_stack.append("CSS3")
    if has_html and not (has_js or has_php or has_py or has_go):
        detected_stack.append("HTML5 (Static Web)")
    if has_dotnet:
        if has_dotnet_framework and not has_dotnet_core:
            detected_stack.append(".NET Framework (C#)")
            test_command = "vstest.console.exe"
            build_command = "nuget restore && msbuild"
        else:
            detected_stack.append(".NET Core (C#)")
            test_command = "dotnet test"
            build_command = "dotnet build"
    if has_docker:
        detected_stack.append("Docker")
    if has_prisma:
        detected_stack.append("Prisma ORM")

    # Defaults if nothing is found
    if not detected_stack:
        detected_stack.append("General Project")
        
    main_stack = None
    if has_py:
        main_stack = "python"
    elif has_js:
        main_stack = "node"
    elif has_php:
        main_stack = "php"
    elif has_dotnet:
        main_stack = "dotnet"

    return {
        "stack": ", ".join(detected_stack),
        "main_stack": main_stack,
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

    content = re.sub(r'Use \*\*.*?\*\* (?:for the main product stack|for all CLI scripting)\.?', f'Use **{scan_results["stack"]}** for the main product stack.', content)
    content = re.sub(r'test command is: `.*?`\.|test command before.*', f'test command is: `{scan_results["test_command"]}`.', content)
    
    with open(rules_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated .agents/rules.md with build and test guidelines.")

def generate_recommendations_report(scan_results):
    os.makedirs(".agents/plans", exist_ok=True)
    report_path = ".agents/plans/recon_recommendations.md"
    
    # 1. Check directories
    missing_dirs = []
    stack = scan_results.get("main_stack")
    if stack == "python":
        for d in ("src", "tests"):
            if not os.path.isdir(d):
                missing_dirs.append(d)
    elif stack == "node":
        for d in ("src", "tests"):
            if not os.path.isdir(d):
                missing_dirs.append(d)
    elif stack == "php":
        for d in ("src", "tests"):
            if not os.path.isdir(d):
                missing_dirs.append(d)

    # 2. Check dependencies
    missing_deps = []
    suggested_cmds = []
    
    if stack == "python":
        reqs_file = "requirements.txt"
        has_test = False
        has_lint = False
        if os.path.exists(reqs_file):
            try:
                with open(reqs_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                if "pytest" in content or "unittest" in content:
                    has_test = True
                if "flake8" in content or "black" in content or "pylint" in content:
                    has_lint = True
            except Exception:
                pass
        if not has_test:
            missing_deps.append("pytest")
            suggested_cmds.append("pip install pytest")
        if not has_lint:
            missing_deps.append("flake8")
            suggested_cmds.append("pip install flake8")
            
    elif stack == "node":
        pkg_file = "package.json"
        has_test = False
        has_lint = False
        if os.path.exists(pkg_file):
            try:
                import json
                with open(pkg_file, 'r', encoding='utf-8') as f:
                    p_data = json.load(f)
                dev_deps = p_data.get("devDependencies", {})
                deps = p_data.get("dependencies", {})
                all_deps = {**dev_deps, **deps}
                for k in all_deps:
                    if k in ("jest", "mocha", "vitest", "jasmine"):
                        has_test = True
                    if k in ("eslint", "prettier"):
                        has_lint = True
            except Exception:
                pass
        if not has_test:
            missing_deps.append("jest")
            suggested_cmds.append("npm install --save-dev jest")
        if not has_lint:
            missing_deps.append("eslint")
            suggested_cmds.append("npm install --save-dev eslint")
            
    elif stack == "php":
        comp_file = "composer.json"
        has_test = False
        if os.path.exists(comp_file):
            try:
                import json
                with open(comp_file, 'r', encoding='utf-8') as f:
                    p_data = json.load(f)
                dev_deps = p_data.get("require-dev", {})
                deps = p_data.get("require", {})
                all_deps = {**dev_deps, **deps}
                if any("phpunit" in k or "pest" in k for k in all_deps):
                    has_test = True
            except Exception:
                pass
        if not has_test:
            missing_deps.append("phpunit/phpunit")
            suggested_cmds.append("composer require --dev phpunit/phpunit")

    # 3. Check gitignore
    missing_ignores = []
    gitignore_file = ".gitignore"
    ignores_to_check = []
    if stack == "python":
        ignores_to_check = ["venv/", "__pycache__/", ".pytest_cache/"]
    elif stack == "node":
        ignores_to_check = ["node_modules/", "dist/"]
    elif stack == "php":
        ignores_to_check = ["vendor/"]
    elif stack == "dotnet":
        ignores_to_check = ["bin/", "obj/", "*.user", "*.suo", ".vs/"]
        
    if os.path.exists(gitignore_file) and ignores_to_check:
        try:
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                git_content = f.read()
            for pattern in ignores_to_check:
                if pattern not in git_content:
                    missing_ignores.append(pattern)
        except Exception:
            pass
    elif not os.path.exists(gitignore_file) and ignores_to_check:
        missing_ignores = ignores_to_check
        suggested_cmds.append("touch .gitignore")

    # Write report
    report_content = f"""# Workspace Auto-Reconnaissance Recommendations

This report is automatically generated by `recon.py`. It lists recommended structural changes and missing dependencies for the active project stack.

## 1. Detected Stack
- **Primary Stack**: {scan_results.get("stack", "General Project")}

"""
    if missing_dirs:
        report_content += "## 2. Missing Standard Directories\n"
        for d in missing_dirs:
            report_content += f"- [ ] `{d}/` directory is missing.\n"
        report_content += "\n"
    else:
        report_content += "## 2. Directory Structure\n- [x] All standard directories are present.\n\n"

    if missing_deps:
        report_content += "## 3. Missing Developer Dependencies\n"
        for dep in missing_deps:
            report_content += f"- [ ] `{dep}` is not installed or configured.\n"
        report_content += "\n"
    else:
        report_content += "## 3. Developer Dependencies\n- [x] Recommended test and lint dependencies are configured.\n\n"

    if missing_ignores:
        report_content += "## 4. Missing Gitignore Patterns\n"
        for pattern in missing_ignores:
            report_content += f"- [ ] `{pattern}` pattern is missing from `.gitignore`.\n"
        report_content += "\n"
    else:
        report_content += "## 4. Gitignore Configuration\n- [x] `.gitignore` contains all standard ignore patterns.\n\n"

    if suggested_cmds:
        report_content += "## 5. Suggested Recovery Commands\n"
        for cmd in suggested_cmds:
            report_content += f"```bash\n{cmd}\n```\n"
        report_content += "\n"
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"Generated structured recommendations report at '{report_path}'.")

def setup_projects_json(scan_results):
    projects_file = ".agents/projects.json"
    should_write = True
    if os.path.exists(projects_file):
        try:
            import json
            with open(projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            projects = data.get("projects", [])
            if projects:
                first_proj = projects[0]
                if first_proj.get("path") not in ("app/backend", "app/frontend"):
                    should_write = False
        except Exception:
            pass
            
    if should_write:
        main_stack = scan_results.get("main_stack") or "general"
        test_command = scan_results.get("test_command")
        if test_command and test_command != "N/A":
            import json
            proj_data = {
                "projects": [
                    {
                        "name": "main-project",
                        "path": ".",
                        "stack": main_stack,
                        "test_command": test_command,
                        "description": f"Auto-detected {scan_results.get('stack')} project."
                    }
                ]
            }
            try:
                os.makedirs(os.path.dirname(projects_file), exist_ok=True)
                with open(projects_file, 'w', encoding='utf-8') as f:
                    json.dump(proj_data, f, indent=2)
                print(f"Configured {projects_file} with detected root project.")
            except Exception as e:
                print(f"Warning: Failed to write {projects_file}: {e}")

if __name__ == '__main__':
    print("Running enterprise auto-reconnaissance scan...")
    results = scan_workspace()
    print(f"Detected Stack: {results['stack']}")
    print(f"Recommended Test: {results['test_command']}")
    
    update_agents_md(results)
    update_rules_md(results)
    generate_recommendations_report(results)
    setup_projects_json(results)
    print("Auto-reconnaissance completed successfully!")
