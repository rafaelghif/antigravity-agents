import os
import re
import sys
from typing import Dict, List, Set, Optional, Any

def detect_dotnet(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects .NET and .NET Core projects, classifying WPF, WinForms, and ASP.NET."""
    has_csproj = any(f.endswith('.csproj') for f in file_names)
    has_sln = any(f.endswith('.sln') for f in file_names)
    has_cs = any(f.endswith('.cs') for f in file_names)
    
    if not (has_csproj or has_sln or has_cs):
        return None
        
    is_core = True
    is_framework = False
    sub_frameworks: List[str] = []
    
    for path, content in file_contents.items():
        if path.endswith('.csproj'):
            if '<TargetFrameworkVersion>v' in content:
                is_framework = True
                is_core = False
            elif '<TargetFramework>' in content or 'Sdk="Microsoft.NET.Sdk' in content:
                is_core = True
                is_framework = False
            
            if '<UseWPF>true</UseWPF>' in content or 'PresentationFramework' in content:
                sub_frameworks.append("WPF")
            if '<UseWindowsForms>true</UseWindowsForms>' in content or 'System.Windows.Forms' in content:
                sub_frameworks.append("WinForms")
            if 'Sdk="Microsoft.NET.Sdk.Web"' in content or 'Microsoft.AspNetCore' in content:
                sub_frameworks.append("ASP.NET Core")
            if 'System.Web.Mvc' in content or 'System.Web.Http' in content:
                sub_frameworks.append("ASP.NET MVC")
                
    sub_frameworks = list(set(sub_frameworks))
    
    test_framework = "xUnit"
    csproj_contents = "".join(file_contents[p] for p in file_contents if p.endswith('.csproj'))
    if "nunit" in csproj_contents.lower():
        test_framework = "NUnit"
    elif "mstest" in csproj_contents.lower() or "visualstudio.testtools" in csproj_contents.lower():
        test_framework = "MSTest"
        
    # Architectural Recommendation
    if any(f in ("WPF", "WinForms") for f in sub_frameworks) and not any(f in ("ASP.NET Core", "ASP.NET MVC") for f in sub_frameworks):
        arch = "Desktop layered architecture (MVVM/MVP)"
    else:
        arch = "Clean Architecture / Domain-Driven Design (DDD)"
        
    if is_framework:
        name = ".NET Framework (C#)"
        if sub_frameworks:
            name += f" [{', '.join(sub_frameworks)}]"
        return {
            "name": name,
            "main_stack": "dotnet",
            "test_command": "vstest.console.exe",
            "build_command": "nuget restore && msbuild",
            "lint_command": "dotnet format --verify-no-changes",
            "recommended_architecture": arch
        }
    else:
        name = ".NET Core (C#)"
        if sub_frameworks:
            name += f" [{', '.join(sub_frameworks)}]"
        return {
            "name": name,
            "main_stack": "dotnet",
            "test_command": "dotnet test",
            "build_command": "dotnet build",
            "lint_command": "dotnet format --verify-no-changes",
            "recommended_architecture": arch
        }

def detect_php(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects PHP projects and frameworks like Laravel, Symfony, and WordPress, adapting tests to Pest/PHPUnit."""
    has_php_files = any(f.endswith('.php') for f in file_names)
    has_composer = 'composer.json' in file_names
    
    if not (has_php_files or has_composer):
        return None
        
    is_laravel = 'artisan' in file_names
    is_symfony = 'symfony.lock' in file_names
    is_wordpress = 'wp-config.php' in file_names or any('wp-content' in p for p in file_paths)
    
    composer_content = ""
    for path, content in file_contents.items():
        if path.endswith('composer.json'):
            composer_content = content
            break
            
    if not is_laravel and "laravel/framework" in composer_content:
        is_laravel = True
    if not is_symfony and "symfony/" in composer_content:
        is_symfony = True
        
    framework = ""
    arch = "MVC (Model-View-Controller)"
    if is_laravel:
        framework = "Laravel"
        arch = "MVC (Model-View-Controller) / Clean Architecture"
    elif is_symfony:
        framework = "Symfony"
        arch = "MVC (Model-View-Controller) / Clean Architecture"
    elif is_wordpress:
        framework = "WordPress"
        arch = "Hooks-based Plugin/Theme Architecture"
        
    has_pest = "pestphp/pest" in composer_content
    has_phpunit = "phpunit/phpunit" in composer_content or any(f in ('phpunit.xml', 'phpunit.xml.dist') for f in file_names)
    
    if is_laravel:
        test_cmd = "php artisan test"
    elif has_pest:
        test_cmd = "./vendor/bin/pest"
    elif has_phpunit:
        test_cmd = "./vendor/bin/phpunit"
    else:
        test_cmd = "./vendor/bin/phpunit"
            
    name = "PHP"
    if framework:
        name += f" ({framework})"
        
    return {
        "name": name,
        "main_stack": "php",
        "test_command": test_cmd,
        "build_command": "composer install",
        "lint_command": "./vendor/bin/phpcs" if 'phpcs' in composer_content else "php -l",
        "recommended_architecture": arch
    }

def detect_js_ts(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects JavaScript/TypeScript projects, frameworks like React, Vue, NestJS, and packages managers like npm/yarn/pnpm/bun."""
    has_js_ts_files = any(f.endswith(('.js', '.ts', '.jsx', '.tsx')) for f in file_names)
    has_pkg_json = 'package.json' in file_names
    
    if not (has_js_ts_files or has_pkg_json):
        return None
        
    pkg_content = ""
    for path, content in file_contents.items():
        if path.endswith('package.json'):
            pkg_content = content
            break
            
    build_tool = "npm"
    build_cmd = "npm run build"
    test_cmd = "npm run test"
    lint_cmd = "npm run lint"
    
    if 'yarn.lock' in file_names:
        build_tool = "yarn"
        build_cmd = "yarn build"
        test_cmd = "yarn test"
        lint_cmd = "yarn lint"
    elif 'pnpm-lock.yaml' in file_names:
        build_tool = "pnpm"
        build_cmd = "pnpm build"
        test_cmd = "pnpm test"
        lint_cmd = "pnpm lint"
    elif 'bun.lockb' in file_names:
        build_tool = "bun"
        build_cmd = "bun run build"
        test_cmd = "bun test"
        lint_cmd = "bun run lint"
        
    frameworks: List[str] = []
    arch = "Layered (Controller-Service-Repository) / MVC"
    
    if "next" in pkg_content:
        frameworks.append("Next.js")
        arch = "Component-driven / App Router Layered"
    if "nuxt" in pkg_content:
        frameworks.append("Nuxt")
        arch = "Component-driven / App Router Layered"
    if "express" in pkg_content:
        frameworks.append("Express")
    if "@nestjs/core" in pkg_content:
        frameworks.append("NestJS")
        arch = "Clean Architecture / Domain-Driven Design (DDD) / Modular"
    if "react" in pkg_content and "next" not in pkg_content:
        frameworks.append("React")
        arch = "Atomic Design / Component-driven"
    if "vue" in pkg_content and "nuxt" not in pkg_content:
        frameworks.append("Vue")
        arch = "Atomic Design / Component-driven"
    if "@angular/core" in pkg_content:
        frameworks.append("Angular")
        arch = "Component-driven Layered Architecture"
        
    is_ts = "typescript" in pkg_content or any(f.endswith(('.ts', '.tsx')) for f in file_names)
    
    stack_name = "TypeScript" if is_ts else "JavaScript"
    if frameworks:
        stack_name += f" ({', '.join(frameworks)})"
        
    return {
        "name": f"{stack_name} (Node.js)",
        "main_stack": "node",
        "build_tool": build_tool,
        "test_command": test_cmd,
        "build_command": f"{build_tool} install" if not has_js_ts_files else build_cmd,
        "lint_command": lint_cmd,
        "recommended_architecture": arch
    }

def detect_python(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Python projects, web frameworks, and unit testing runner."""
    has_py_files = any(f.endswith('.py') for f in file_names)
    has_reqs = 'requirements.txt' in file_names
    has_pyproject = 'pyproject.toml' in file_names
    
    if not (has_py_files or has_reqs or has_pyproject):
        return None
        
    is_django = 'manage.py' in file_names
    is_flask = False
    is_fastapi = False
    
    reqs_content = ""
    for path, content in file_contents.items():
        if path.endswith(('requirements.txt', 'pyproject.toml', 'Pipfile')):
            reqs_content += "\n" + content
            
    if "django" in reqs_content.lower():
        is_django = True
    if "flask" in reqs_content.lower():
        is_flask = True
    if "fastapi" in reqs_content.lower():
        is_fastapi = True
        
    framework = ""
    arch = "Layered Architecture"
    if is_django:
        framework = "Django"
        arch = "MVC (Model-View-Template)"
    elif is_flask:
        framework = "Flask"
        arch = "Layered (Controller-Service-Repository) / Hexagonal (Ports & Adapters)"
    elif is_fastapi:
        framework = "FastAPI"
        arch = "Layered (Controller-Service-Repository) / Hexagonal (Ports & Adapters)"
        
    has_pytest = "pytest" in reqs_content.lower() or any('test' in f and 'py' in f for f in file_names)
    
    test_cmd = "pytest" if has_pytest else "python -m unittest"
    build_cmd = "pip install -r requirements.txt" if has_reqs else "pip install ."
    
    name = "Python 3"
    if framework:
        name += f" ({framework})"
        
    return {
        "name": name,
        "main_stack": "python",
        "test_command": test_cmd,
        "build_command": build_cmd,
        "lint_command": "flake8 .",
        "recommended_architecture": arch
    }

def detect_go(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Go projects and popular web frameworks."""
    has_go_files = any(f.endswith('.go') for f in file_names)
    has_go_mod = 'go.mod' in file_names
    
    if not (has_go_files or has_go_mod):
        return None
        
    go_mod_content = ""
    for path, content in file_contents.items():
        if path.endswith('go.mod'):
            go_mod_content = content
            break
            
    frameworks: List[str] = []
    if "github.com/gin-gonic/gin" in go_mod_content:
        frameworks.append("Gin")
    if "github.com/labstack/echo" in go_mod_content:
        frameworks.append("Echo")
    if "github.com/gofiber/fiber" in go_mod_content:
        frameworks.append("Fiber")
    if "github.com/astaxie/beego" in go_mod_content or "github.com/beego/beego" in go_mod_content:
        frameworks.append("Beego")
        
    name = "Go (Golang)"
    if frameworks:
        name += f" ({', '.join(frameworks)})"
        
    return {
        "name": name,
        "main_stack": "go",
        "test_command": "go test ./...",
        "build_command": "go build",
        "lint_command": "golangci-lint run",
        "recommended_architecture": "Layered (Controller-Service-Repository) / Hexagonal"
    }

def detect_rust(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Rust projects and web frameworks."""
    has_rs_files = any(f.endswith('.rs') for f in file_names)
    has_cargo = 'Cargo.toml' in file_names
    
    if not (has_rs_files or has_cargo):
        return None
        
    cargo_content = ""
    for path, content in file_contents.items():
        if path.endswith('Cargo.toml'):
            cargo_content = content
            break
            
    frameworks: List[str] = []
    if "actix-web" in cargo_content:
        frameworks.append("Actix-web")
    if "axum" in cargo_content:
        frameworks.append("Axum")
    if "rocket" in cargo_content:
        frameworks.append("Rocket")
        
    name = "Rust"
    if frameworks:
        name += f" ({', '.join(frameworks)})"
        
    return {
        "name": name,
        "main_stack": "rust",
        "test_command": "cargo test",
        "build_command": "cargo build",
        "lint_command": "cargo clippy",
        "recommended_architecture": "Layered Architecture (Hexagonal / Clean)"
    }

def detect_java_kotlin(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Java or Kotlin projects and Spring Boot / Quarkus frameworks."""
    has_java = any(f.endswith('.java') for f in file_names)
    has_kt = any(f.endswith('.kt') for f in file_names)
    has_pom = 'pom.xml' in file_names
    has_gradle = any(f in ('build.gradle', 'build.gradle.kts') for f in file_names)
    
    if not (has_java or has_kt or has_pom or has_gradle):
        return None
        
    build_content = ""
    for path, content in file_contents.items():
        if path.endswith(('pom.xml', 'build.gradle', 'build.gradle.kts')):
            build_content += "\n" + content
            
    frameworks: List[str] = []
    arch = "Layered Architecture"
    if "spring-boot" in build_content or "springboot" in build_content:
        frameworks.append("Spring Boot")
        arch = "Clean Architecture / Domain-Driven Design (DDD) / Hexagonal"
    if "quarkus" in build_content:
        frameworks.append("Quarkus")
        arch = "Clean Architecture / Domain-Driven Design (DDD) / Hexagonal"
    if "micronaut" in build_content:
        frameworks.append("Micronaut")
        arch = "Clean Architecture / Domain-Driven Design (DDD) / Hexagonal"
        
    lang = "Java"
    if has_kt and not has_java:
        lang = "Kotlin"
    elif has_kt and has_java:
        lang = "Java/Kotlin"
        
    name = lang
    if frameworks:
        name += f" ({', '.join(frameworks)})"
        
    if has_pom:
        return {
            "name": name,
            "main_stack": "java",
            "test_command": "mvn test",
            "build_command": "mvn clean package",
            "lint_command": "mvn checkstyle:check",
            "recommended_architecture": arch
        }
    else:
        gradlew = "./gradlew" if any('gradlew' in f for f in file_names) else "gradle"
        return {
            "name": name,
            "main_stack": "java",
            "test_command": f"{gradlew} test",
            "build_command": f"{gradlew} build",
            "lint_command": f"{gradlew} check",
            "recommended_architecture": arch
        }

def detect_ruby(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Ruby projects and Rails/Sinatra frameworks, adapting test runner to RSpec/Minitest."""
    has_rb = any(f.endswith('.rb') for f in file_names)
    has_gemfile = 'Gemfile' in file_names
    
    if not (has_rb or has_gemfile):
        return None
        
    gemfile_content = ""
    for path, content in file_contents.items():
        if path.endswith('Gemfile'):
            gemfile_content = content
            break
            
    is_rails = 'config/application.rb' in file_paths or 'rails' in gemfile_content
    is_sinatra = 'sinatra' in gemfile_content
    
    framework = ""
    arch = "Modular / Layered Architecture"
    if is_rails:
        framework = "Ruby on Rails"
        arch = "MVC (Model-View-Controller)"
    elif is_sinatra:
        framework = "Sinatra"
        
    name = "Ruby"
    if framework:
        name += f" ({framework})"
        
    has_rspec = "rspec" in gemfile_content or 'spec' in file_names or any('spec/' in p for p in file_paths)
    
    if has_rspec:
        test_cmd = "bundle exec rspec"
    else:
        test_cmd = "bundle exec rake test"
        
    return {
        "name": name,
        "main_stack": "ruby",
        "test_command": test_cmd,
        "build_command": "bundle install",
        "lint_command": "bundle exec rubocop",
        "recommended_architecture": arch
    }

def detect_dart(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Dart and Flutter projects."""
    has_dart = any(f.endswith('.dart') for f in file_names)
    has_pubspec = 'pubspec.yaml' in file_names
    
    if not (has_dart or has_pubspec):
        return None
        
    pubspec_content = ""
    for path, content in file_contents.items():
        if path.endswith('pubspec.yaml'):
            pubspec_content = content
            break
            
    is_flutter = "flutter:" in pubspec_content or "sdk: flutter" in pubspec_content
    
    name = "Dart (Flutter)" if is_flutter else "Dart"
    test_cmd = "flutter test" if is_flutter else "dart test"
    build_cmd = "flutter build apk" if is_flutter else "dart pub get"
    arch = "BLoC / Feature-First Layered Architecture" if is_flutter else "Layered Architecture"
    
    return {
        "name": name,
        "main_stack": "dart",
        "test_command": test_cmd,
        "build_command": build_cmd,
        "lint_command": "flutter analyze" if is_flutter else "dart analyze",
        "recommended_architecture": arch
    }

def detect_elixir(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Elixir and Phoenix framework projects."""
    has_ex = any(f.endswith(('.ex', '.exs')) for f in file_names)
    has_mix = 'mix.exs' in file_names
    
    if not (has_ex or has_mix):
        return None
        
    mix_content = ""
    for path, content in file_contents.items():
        if path.endswith('mix.exs'):
            mix_content = content
            break
            
    is_phoenix = "phoenix" in mix_content
    
    name = "Elixir (Phoenix)" if is_phoenix else "Elixir"
    arch = "MVC (Model-View-Controller) / Context-driven" if is_phoenix else "Functional/Modular Architecture"
    
    return {
        "name": name,
        "main_stack": "elixir",
        "test_command": "mix test",
        "build_command": "mix deps.get",
        "lint_command": "mix format --check-formatted",
        "recommended_architecture": arch
    }

def detect_swift(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects Swift and Vapor projects."""
    has_swift = any(f.endswith('.swift') for f in file_names)
    has_pkg = 'Package.swift' in file_names
    
    if not (has_swift or has_pkg):
        return None
        
    pkg_content = ""
    for path, content in file_contents.items():
        if path.endswith('Package.swift'):
            pkg_content = content
            break
            
    is_vapor = "vapor" in pkg_content.lower()
    
    name = "Swift (Vapor)" if is_vapor else "Swift"
    arch = "MVC (Model-View-Controller)" if is_vapor else "MVVM (Model-View-ViewModel)"
    
    return {
        "name": name,
        "main_stack": "swift",
        "test_command": "swift test",
        "build_command": "swift build",
        "lint_command": "swiftlint",
        "recommended_architecture": arch
    }

def detect_cpp(file_names: Set[str], file_paths: List[str], file_contents: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Detects C++ projects using CMake or Makefiles."""
    cpp_exts = ('.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx')
    has_cpp = any(f.endswith(cpp_exts) for f in file_names)
    has_cmake = 'CMakeLists.txt' in file_names
    has_makefile = 'Makefile' in file_names
    
    if not (has_cpp or has_cmake or has_makefile):
        return None
        
    name = "C++"
    if has_cmake:
        return {
            "name": name,
            "main_stack": "cpp",
            "test_command": "ctest",
            "build_command": "cmake -B build && cmake --build build",
            "lint_command": "clang-tidy",
            "recommended_architecture": "Modular Library / Layered Architecture"
        }
    else:
        return {
            "name": name,
            "main_stack": "cpp",
            "test_command": "make test",
            "build_command": "make",
            "lint_command": "cppcheck .",
            "recommended_architecture": "Modular Architecture"
        }

def scan_workspace() -> Dict[str, Any]:
    """Scans the workspace directory to auto-detect target stack and dependencies."""
    file_paths: List[str] = []
    file_names: Set[str] = set()
    file_contents: Dict[str, str] = {}
    
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', '.pytest_cache', 'vendor', '.agents', '.lock', 'logs', 'dist', 'build', 'out'}
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), '.')
            file_paths.append(rel_path)
            file_names.add(file)
            
            lower_file = file.lower()
            if (file in ('package.json', 'composer.json', 'Gemfile', 'pubspec.yaml', 'mix.exs', 'pom.xml', 'build.gradle', 'build.gradle.kts', 'CMakeLists.txt', 'Package.swift', 'go.mod', 'Cargo.toml', 'requirements.txt', 'pyproject.toml', 'Pipfile') or 
                file.endswith('.csproj') or file.endswith('.sln') or file == 'manage.py'):
                try:
                    with open(rel_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_contents[rel_path] = f.read()
                except Exception:
                    pass

    detections: List[Dict[str, Any]] = []
    
    # Run all detectors
    dotnet_res = detect_dotnet(file_names, file_paths, file_contents)
    if dotnet_res:
        detections.append(dotnet_res)
        
    php_res = detect_php(file_names, file_paths, file_contents)
    if php_res:
        detections.append(php_res)
        
    node_res = detect_js_ts(file_names, file_paths, file_contents)
    if node_res:
        detections.append(node_res)
        
    py_res = detect_python(file_names, file_paths, file_contents)
    if py_res:
        detections.append(py_res)
        
    go_res = detect_go(file_names, file_paths, file_contents)
    if go_res:
        detections.append(go_res)
        
    rust_res = detect_rust(file_names, file_paths, file_contents)
    if rust_res:
        detections.append(rust_res)
        
    java_res = detect_java_kotlin(file_names, file_paths, file_contents)
    if java_res:
        detections.append(java_res)
        
    ruby_res = detect_ruby(file_names, file_paths, file_contents)
    if ruby_res:
        detections.append(ruby_res)
        
    dart_res = detect_dart(file_names, file_paths, file_contents)
    if dart_res:
        detections.append(dart_res)
        
    elixir_res = detect_elixir(file_names, file_paths, file_contents)
    if elixir_res:
        detections.append(elixir_res)
        
    swift_res = detect_swift(file_names, file_paths, file_contents)
    if swift_res:
        detections.append(swift_res)
        
    cpp_res = detect_cpp(file_names, file_paths, file_contents)
    if cpp_res:
        detections.append(cpp_res)

    auxiliary: List[str] = []
    if any('tailwind.config' in f for f in file_names):
        auxiliary.append("Tailwind CSS")
    elif any(f.endswith(('.css', '.scss', '.sass')) for f in file_names) and not any('tailwind.config' in f for f in file_names):
        auxiliary.append("CSS3")
        
    if any(f.endswith('.html') for f in file_names) and not any(d["main_stack"] in ("php", "node", "python", "go") for d in detections):
        auxiliary.append("HTML5 (Static Web)")
        
    if 'Dockerfile' in file_names or 'docker-compose.yml' in file_names:
        auxiliary.append("Docker")
        
    if any('prisma' in f.lower() or 'schema.prisma' in f for f in file_names):
        auxiliary.append("Prisma ORM")

    detected_stack = [d["name"] for d in detections] + auxiliary
    if not detected_stack:
        detected_stack = ["General Project"]

    primary_detection = None
    if detections:
        priority = ["dotnet", "php", "node", "python", "go", "rust", "java", "ruby", "dart", "elixir", "swift", "cpp"]
        for p in priority:
            for d in detections:
                if d["main_stack"] == p:
                    primary_detection = d
                    break
            if primary_detection:
                break
        if not primary_detection:
            primary_detection = detections[0]

    if primary_detection:
        main_stack = primary_detection["main_stack"]
        build_tool = primary_detection.get("build_tool")
        test_command = primary_detection["test_command"]
        lint_command = primary_detection["lint_command"]
        build_command = primary_detection["build_command"]
        recommended_architecture = primary_detection["recommended_architecture"]
    else:
        main_stack = None
        build_tool = None
        test_command = "N/A"
        lint_command = "N/A"
        build_command = "N/A"
        recommended_architecture = "Layered Architecture"

    return {
        "stack": ", ".join(detected_stack),
        "main_stack": main_stack,
        "build_tool": build_tool,
        "test_command": test_command,
        "lint_command": lint_command,
        "build_command": build_command,
        "recommended_architecture": recommended_architecture
    }

def update_agents_md(scan_results: Dict[str, Any]) -> None:
    """Updates AGENTS.md with detected stack info."""
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

def update_rules_md(scan_results: Dict[str, Any]) -> None:
    """Updates .agents/rules.md with stack build and test commands."""
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

def generate_recommendations_report(scan_results: Dict[str, Any]) -> None:
    """Generates a recommendations report for missing directories, dependencies, or gitignores."""
    os.makedirs(".agents/plans", exist_ok=True)
    report_path = ".agents/plans/recon_recommendations.md"
    
    # 1. Check directories
    missing_dirs: List[str] = []
    stack = scan_results.get("main_stack")
    if stack in ("python", "node", "php", "go", "rust", "ruby", "elixir", "cpp"):
        for d in ("src", "tests"):
            if not os.path.isdir(d):
                missing_dirs.append(d)
    elif stack == "dart":
        for d in ("lib", "test"):
            if not os.path.isdir(d):
                missing_dirs.append(d)
    elif stack == "swift":
        for d in ("Sources", "Tests"):
            if not os.path.isdir(d):
                missing_dirs.append(d)
    elif stack == "java":
        for d in ("src/main/java", "src/test/java"):
            if not os.path.isdir(d):
                missing_dirs.append(d)

    # 2. Check dependencies
    missing_deps: List[str] = []
    suggested_cmds: List[str] = []
    
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
    missing_ignores: List[str] = []
    gitignore_file = ".gitignore"
    ignores_to_check: List[str] = []
    if stack == "python":
        ignores_to_check = ["venv/", "__pycache__/", ".pytest_cache/"]
    elif stack == "node":
        ignores_to_check = ["node_modules/", "dist/"]
    elif stack == "php":
        ignores_to_check = ["vendor/"]
    elif stack == "dotnet":
        ignores_to_check = ["bin/", "obj/", "*.user", "*.suo", ".vs/"]
    elif stack == "ruby":
        ignores_to_check = ["vendor/bundle/", ".bundle/"]
    elif stack == "go":
        ignores_to_check = ["bin/"]
    elif stack == "rust":
        ignores_to_check = ["target/"]
    elif stack == "java":
        ignores_to_check = ["target/", ".gradle/", "build/"]
    elif stack == "elixir":
        ignores_to_check = ["_build/", "deps/"]
    elif stack == "swift":
        ignores_to_check = [".build/", ".swiftdoc/"]
    elif stack == "dart":
        ignores_to_check = [".dart_tool/", "build/"]
    elif stack == "cpp":
        ignores_to_check = ["build/", "bin/"]
        
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
- **Recommended Architecture**: {scan_results.get("recommended_architecture", "N/A")}

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

def setup_projects_json(scan_results: Dict[str, Any]) -> None:
    """Configures .agents/projects.json using detected project stack."""
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
    print(f"Recommended Architecture: {results['recommended_architecture']}")
    
    update_agents_md(results)
    update_rules_md(results)
    generate_recommendations_report(results)
    setup_projects_json(results)
    print("Auto-reconnaissance completed successfully!")
