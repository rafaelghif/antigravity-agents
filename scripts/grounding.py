#!/usr/bin/env python3
"""
AAC Epistemic Grounding Engine:
Pre-Action Reality Check to Eliminate Hallucinations.
Inspects the actual workspace to extract detected languages, package managers,
declared dependencies, existing project layouts, and git state before any agent acts.
Supports all major languages: Python, TS/JS, Go, Rust, Java/Kotlin, C#, PHP, Ruby, Dart/Flutter, C/C++, Elixir, Swift.
"""
from __future__ import annotations

import json, os, platform, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST_CONFIGS = {
    "node": ["package.json"],
    "python": ["pyproject.toml", "requirements.txt", "Pipfile", "setup.py"],
    "rust": ["Cargo.toml"],
    "go": ["go.mod"],
    "java_maven": ["pom.xml"],
    "java_gradle": ["build.gradle", "build.gradle.kts"],
    "dotnet": ["*.csproj", "*.sln"],
    "php": ["composer.json"],
    "ruby": ["Gemfile"],
    "dart_flutter": ["pubspec.yaml"],
    "elixir": ["mix.exs"],
    "swift": ["Package.swift"],
    "cpp": ["CMakeLists.txt", "Makefile"],
}

EXT_TO_ECO: dict[str, str] = {
    ".ts": "node", ".tsx": "node", ".js": "node", ".jsx": "node",
    ".py": "python",
    ".rs": "rust",
    ".go": "go",
    ".java": "java_maven",
    ".cs": "dotnet",
    ".php": "php",
    ".rb": "ruby",
    ".dart": "dart_flutter",
    ".ex": "elixir", ".exs": "elixir",
    ".swift": "swift",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "cpp", ".h": "cpp", ".hpp": "cpp",
}

SCAN_EXCLUDES = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".agents-backups", "target"}

def _match_pattern_in_dir(directory: Path, prefix: str, pat: str) -> list[str]:
    if "*" in pat:
        return [f"{prefix}/{m.name}" for m in directory.glob(pat)]
    if (directory / pat).is_file():
        return [f"{prefix}/{pat}"]
    return []

def _check_dir_for_patterns(directory: Path, prefix: str, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pat in patterns:
        found.extend(_match_pattern_in_dir(directory, prefix, pat))
    return found

def _check_grandchild_dirs(parent: Path, patterns: list[str]) -> list[str]:
    found: list[str] = []
    try:
        subs = [s for s in sorted(parent.iterdir()) if s.is_dir() and s.name not in SCAN_EXCLUDES and not s.name.startswith(".")]
        for sub in subs:
            found.extend(_check_dir_for_patterns(sub, f"{parent.name}/{sub.name}", patterns))
    except Exception as e:
        sys.stderr.write(f"Grounding grandchild scan notice: {e}\n")
    return found

def _check_subdirectories_for_patterns(root: Path, patterns: list[str]) -> list[str]:
    found: list[str] = []
    try:
        children = [c for c in sorted(root.iterdir()) if c.is_dir() and c.name not in SCAN_EXCLUDES and not c.name.startswith(".")]
        for child in children:
            found.extend(_check_dir_for_patterns(child, child.name, patterns))
            if child.name in ("apps", "packages", "services", "modules") and len(found) < 10:
                found.extend(_check_grandchild_dirs(child, patterns))
    except Exception as e:
        sys.stderr.write(f"Grounding scan notice: {e}\n")
    return found

def _find_eco_manifests(root: Path, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pat in patterns:
        if "*" in pat:
            matches = list(root.glob(pat))
            found.extend(m.name for m in matches)
        elif (root / pat).is_file():
            found.append(pat)
            
    if found:
        return found

    return _check_subdirectories_for_patterns(root, patterns)

def _tally_file_extension(counts: dict[str, int], filename: str) -> None:
    ext = Path(filename).suffix.lower()
    eco = EXT_TO_ECO.get(ext)
    if eco:
        counts[eco] = counts.get(eco, 0) + 1

def _process_dir_files(counts: dict[str, int], filenames: list[str]) -> None:
    for f in filenames:
        _tally_file_extension(counts, f)

def _infer_ecosystems_from_sources(root: Path) -> dict[str, list[str]]:
    inferred: dict[str, list[str]] = {}
    counts: dict[str, int] = {}
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SCAN_EXCLUDES and not d.startswith(".")]
            _process_dir_files(counts, filenames)
    except Exception as e:
        sys.stderr.write(f"Grounding source inference notice: {e}\n")

    for eco, count in counts.items():
        if count > 0:
            inferred[eco] = [f"source files ({count} files)"]
    return inferred

def detect_ecosystems(root: Path) -> dict[str, list[str]]:
    detected = {}
    for eco, patterns in MANIFEST_CONFIGS.items():
        found = _find_eco_manifests(root, patterns)
        if found:
            detected[eco] = found
            
    if not detected:
        detected = _infer_ecosystems_from_sources(root)
        
    return detected

def _parse_req_file(req_txt: Path) -> list[str]:
    deps: list[str] = []
    try:
        for line in req_txt.read_text(encoding="utf-8").splitlines():
            clean = line.strip().split("#")[0].split("==")[0].split(">=")[0].strip()
            if clean and not clean.startswith("-"):
                deps.append(clean)
    except Exception as e:
        sys.stderr.write(f"Grounding notice ({req_txt.name}): {e}\n")
    return deps

def _clean_dep_string(raw: str) -> str:
    clean = re.split(r"[<>=!~;\[\s]", raw)[0].strip()
    return clean if clean.lower() not in ("name", "version", "description", "readme", "python") else ""

def _extract_list_deps(items: list[object]) -> list[str]:
    result = []
    for item in items:
        if isinstance(item, str):
            clean = _clean_dep_string(item)
            if clean:
                result.append(clean)
    return result

def _extract_opt_deps(opt_dict: dict[str, object]) -> list[str]:
    result = []
    for opt_list in opt_dict.values():
        if isinstance(opt_list, list):
            result.extend(_extract_list_deps(opt_list))
    return result

def _extract_poetry_group_deps(groups: dict[str, object]) -> list[str]:
    result = []
    for grp in groups.values():
        if isinstance(grp, dict):
            deps = grp.get("dependencies")
            if isinstance(deps, dict):
                result.extend([k for k in deps.keys() if k.lower() != "python"])
    return result

def _parse_pyproject_deps(content: str) -> list[str]:
    deps: list[str] = []
    try:
        import tomllib
        data = tomllib.loads(content)
        proj = data.get("project")
        if isinstance(proj, dict):
            deps.extend(_extract_list_deps(proj.get("dependencies", [])))
            opt = proj.get("optional-dependencies")
            if isinstance(opt, dict):
                deps.extend(_extract_opt_deps(opt))
        tool = data.get("tool", {})
        if isinstance(tool, dict):
            poetry = tool.get("poetry", {})
            if isinstance(poetry, dict):
                p_deps = poetry.get("dependencies", {})
                if isinstance(p_deps, dict):
                    deps.extend([k for k in p_deps.keys() if k.lower() != "python"])
                groups = poetry.get("group", {})
                if isinstance(groups, dict):
                    deps.extend(_extract_poetry_group_deps(groups))
            flit = tool.get("flit", {})
            if isinstance(flit, dict):
                meta = flit.get("metadata", {})
                if isinstance(meta, dict):
                    deps.extend(_extract_list_deps(meta.get("requires", [])))
        return deps
    except Exception as err:
        sys.stderr.write(f"Pyproject parse notice: {err}\n")

    in_deps_section = False
    in_array = False
    for line in content.splitlines():
        line_s = line.strip()
        if line_s.startswith("["):
            sec = line_s.strip("[]").strip()
            in_deps_section = sec in ("project.dependencies", "tool.poetry.dependencies") or "dependencies" in sec
            in_array = False
            continue
        if "dependencies = [" in line_s:
            in_array = True
            continue
        if in_array:
            if "]" in line_s:
                in_array = False
            match = re.search(r'["\']([a-zA-Z0-9_\-\.]+)', line_s)
            if match:
                clean = _clean_dep_string(match.group(1))
                if clean:
                    deps.append(clean)
        elif in_deps_section and "=" in line_s:
            key = line_s.split("=")[0].strip().strip("\"'")
            if key and key.lower() not in ("python", "version", "name", "description", "readme"):
                deps.append(key)
    return deps

def _parse_cargo_deps(content: str) -> list[str]:
    deps: list[str] = []
    try:
        import tomllib
        data = tomllib.loads(content)
        for sec in ("dependencies", "dev-dependencies", "build-dependencies"):
            sec_data = data.get(sec)
            if isinstance(sec_data, dict):
                deps.extend(sec_data.keys())
        ws = data.get("workspace")
        if isinstance(ws, dict):
            ws_deps = ws.get("dependencies")
            if isinstance(ws_deps, dict):
                deps.extend(ws_deps.keys())
        return deps
    except Exception as err:
        sys.stderr.write(f"Cargo parse notice: {err}\n")

    in_deps_section = False
    for line in content.splitlines():
        line_s = line.strip()
        if line_s.startswith("["):
            sec = line_s.strip("[]").strip()
            in_deps_section = sec in ("dependencies", "dev-dependencies", "build-dependencies", "workspace.dependencies")
            continue
        if in_deps_section and "=" in line_s:
            key = line_s.split("=")[0].strip()
            if key and key not in ("package", "dependencies", "dev-dependencies", "name", "version", "edition"):
                deps.append(key)
    return deps

def extract_dependencies(root: Path, ecosystems: dict[str, list[str]]) -> dict[str, list[str]]:
    deps = {}

    # Node
    if "node" in ecosystems:
        node_candidates = [root / "package.json"]
        for item in ecosystems.get("node", []):
            if "package.json" in item and (root / item).is_file():
                node_candidates.append(root / item)
        node_deps = []
        for pkg_file in dict.fromkeys(node_candidates):
            if pkg_file.is_file():
                try:
                    pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
                    d = list((pkg.get("dependencies") or {}).keys())
                    dev_d = list((pkg.get("devDependencies") or {}).keys())
                    peer_d = list((pkg.get("peerDependencies") or {}).keys())
                    node_deps.extend(d + dev_d + peer_d)
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({pkg_file.name}): {e}\n")
        if node_deps:
            framework_keys = {"react", "vue", "next", "nuxt", "svelte", "@angular/core", "express", "fastify", "nest", "@nestjs/core", "astro", "hono"}
            favs = [x for x in node_deps if x in framework_keys or any(x.startswith(f) for f in framework_keys)]
            others = [x for x in node_deps if x not in favs]
            deps["node"] = list(dict.fromkeys(favs + others))[:35]

    # Python
    if "python" in ecosystems:
        py_deps = []
        req_candidates = [root / "requirements.txt"]
        pyproj_candidates = [root / "pyproject.toml"]
        for item in ecosystems.get("python", []):
            candidate = root / item
            if candidate.is_file():
                if candidate.name == "requirements.txt":
                    req_candidates.append(candidate)
                elif candidate.name == "pyproject.toml":
                    pyproj_candidates.append(candidate)

        for req_txt in dict.fromkeys(req_candidates):
            if req_txt.is_file():
                py_deps.extend(_parse_req_file(req_txt))

        for pyproj in dict.fromkeys(pyproj_candidates):
            if pyproj.is_file():
                try:
                    content = pyproj.read_text(encoding="utf-8")
                    py_deps.extend(_parse_pyproject_deps(content))
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({pyproj.name}): {e}\n")

        if py_deps:
            deps["python"] = list(dict.fromkeys(py_deps))[:35]
        else:
            deps["python"] = ["standard library / workspace internal packages"]

    # Go
    if "go" in ecosystems:
        go_candidates = [root / "go.mod"]
        for item in ecosystems.get("go", []):
            if "go.mod" in item and (root / item).is_file():
                go_candidates.append(root / item)
        go_deps = []
        for mod_file in dict.fromkeys(go_candidates):
            if mod_file.is_file():
                try:
                    content = mod_file.read_text(encoding="utf-8")
                    matches = re.findall(r'(?:^\s+|require\s+)([a-zA-Z0-9.\-_/]+)\s+v', content, re.MULTILINE)
                    go_deps.extend(matches)
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({mod_file.name}): {e}\n")
        if go_deps:
            deps["go"] = list(dict.fromkeys(go_deps))[:25]

    # Rust
    if "rust" in ecosystems:
        cargo_candidates = [root / "Cargo.toml"]
        for item in ecosystems.get("rust", []):
            if "Cargo.toml" in item and (root / item).is_file():
                cargo_candidates.append(root / item)
        rust_deps = []
        for cargo_file in dict.fromkeys(cargo_candidates):
            if cargo_file.is_file():
                try:
                    content = cargo_file.read_text(encoding="utf-8")
                    rust_deps.extend(_parse_cargo_deps(content))
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({cargo_file.name}): {e}\n")
        if rust_deps:
            deps["rust"] = list(dict.fromkeys(rust_deps))[:25]

    # PHP
    if "php" in ecosystems:
        php_candidates = [root / "composer.json"]
        for item in ecosystems.get("php", []):
            if "composer.json" in item and (root / item).is_file():
                php_candidates.append(root / item)
        php_deps = []
        for composer_file in dict.fromkeys(php_candidates):
            if composer_file.is_file():
                try:
                    data = json.loads(composer_file.read_text(encoding="utf-8"))
                    reqs = list((data.get("require") or {}).keys())
                    php_deps.extend(reqs)
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({composer_file.name}): {e}\n")
        if php_deps:
            deps["php"] = list(dict.fromkeys(php_deps))[:25]

    return deps

def inspect_project_layout(root: Path) -> dict[str, list[str]]:
    key_dirs = []
    excludes = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".agents-backups"}
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name not in excludes and not child.name.startswith("."):
            key_dirs.append(child.name)
    return {"directories": key_dirs}

def get_git_state(root: Path) -> dict[str, str]:
    state = {"branch": "unknown", "status": "clean"}
    if shutil.which("git") and (root / ".git").is_dir():
        try:
            res_b = subprocess.run(["git", "branch", "--show-current"], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res_b.returncode == 0 and res_b.stdout.strip():
                state["branch"] = res_b.stdout.strip()
            res_s = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res_s.returncode == 0:
                dirty = [l.strip() for l in res_s.stdout.splitlines() if l.strip()]
                state["status"] = f"{len(dirty)} modified file(s)" if dirty else "clean"
        except Exception as e:
            sys.stderr.write(f"Git status notice: {e}\n")
    return state

def detect_environment(root: Path) -> dict[str, str]:
    is_win = sys.platform == "win32"
    shell = os.environ.get("SHELL") or ("powershell/cmd.exe" if is_win else "/bin/bash")
    machine = platform.machine()
    return {
        "os": platform.system(),
        "platform": sys.platform,
        "release": platform.release(),
        "machine": machine,
        "architecture": machine,
        "python": sys.version.split()[0],
        "python_path": sys.executable,
        "shell": shell,
        "path_sep": os.sep,
    }

LOCKFILE_MAP = {
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "bun.lockb": "bun",
    "bun.lock": "bun",
    "Cargo.lock": "cargo",
    "go.sum": "go",
    "composer.lock": "composer",
    "Gemfile.lock": "bundler",
    "poetry.lock": "poetry",
    "Pipfile.lock": "pipenv",
    "uv.lock": "uv",
}

CLI_TOOLS = ["git", "npm", "pnpm", "yarn", "bun", "pip", "pip3", "poetry", "uv", "cargo", "go", "make", "docker"]

def _scan_dir_for_lockfiles(directory: Path) -> list[str]:
    found = []
    for lock_name, mgr in LOCKFILE_MAP.items():
        if (directory / lock_name).is_file():
            found.append(mgr)
    return found

def _find_grandchild_dirs(parent: Path) -> list[Path]:
    try:
        return [g for g in parent.iterdir() if g.is_dir() and g.name not in SCAN_EXCLUDES and not g.name.startswith(".")]
    except Exception as e:
        sys.stderr.write(f"Grandchild dirs notice: {e}\n")
        return []

def _collect_all_candidate_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    dirs = [d for d in root.iterdir() if d.is_dir() and d.name not in SCAN_EXCLUDES and not d.name.startswith(".")]
    extended = list(dirs)
    for sub in dirs:
        if sub.name in ("apps", "packages", "services", "modules"):
            extended.extend(_find_grandchild_dirs(sub))
    return extended

def _scan_dirs_for_lockfiles(dirs: list[Path]) -> list[str]:
    found: list[str] = []
    for d in dirs:
        found.extend(_scan_dir_for_lockfiles(d))
    return found

def detect_package_managers(root: Path) -> dict[str, list[str]]:
    lockfile_mgrs = _scan_dir_for_lockfiles(root)

    candidate_dirs = _collect_all_candidate_dirs(root)
    lockfile_mgrs.extend(_scan_dirs_for_lockfiles(candidate_dirs))

    pkg_json_candidates = [root / "package.json"]
    pkg_json_candidates.extend([s / "package.json" for s in candidate_dirs if (s / "package.json").is_file()])

    for pkg_json in dict.fromkeys(pkg_json_candidates):
        if pkg_json.is_file():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                pm = data.get("packageManager", "")
                if pm:
                    name = pm.split("@")[0].strip()
                    if name and name not in lockfile_mgrs:
                        lockfile_mgrs.append(name)
            except Exception as e:
                sys.stderr.write(f"Grounding packageManager notice: {e}\n")

    available_cli = [t for t in CLI_TOOLS if shutil.which(t)]
    return {
        "lockfile_managed": list(dict.fromkeys(lockfile_mgrs)),
        "available_cli": available_cli,
    }

FRAMEWORK_CATALOG = [
    ("next", "Next.js", "node"),
    ("react", "React", "node"),
    ("vue", "Vue", "node"),
    ("nuxt", "Nuxt", "node"),
    ("@sveltejs/kit", "SvelteKit", "node"),
    ("svelte", "Svelte", "node"),
    ("@angular/core", "Angular", "node"),
    ("astro", "Astro", "node"),
    ("express", "Express", "node"),
    ("fastify", "Fastify", "node"),
    ("@nestjs/core", "NestJS", "node"),
    ("hono", "Hono", "node"),
    ("fastapi", "FastAPI", "python"),
    ("django", "Django", "python"),
    ("flask", "Flask", "python"),
    ("starlette", "Starlette", "python"),
    ("tornado", "Tornado", "python"),
    ("gin-gonic/gin", "Gin", "go"),
    ("labstack/echo", "Echo", "go"),
    ("gofiber/fiber", "Fiber", "go"),
    ("actix-web", "Actix Web", "rust"),
    ("axum", "Axum", "rust"),
    ("rocket", "Rocket", "rust"),
    ("laravel/framework", "Laravel", "php"),
    ("symfony/framework-bundle", "Symfony", "php"),
    ("rails", "Ruby on Rails", "ruby"),
]

def detect_frameworks(root: Path, dependencies: dict[str, list[str]]) -> list[dict[str, str]]:
    found = []
    seen = set()
    for pkg_id, name, eco in FRAMEWORK_CATALOG:
        eco_deps = [d.lower() for d in dependencies.get(eco, [])]
        if any(pkg_id.lower() in d for d in eco_deps):
            if name not in seen:
                seen.add(name)
                found.append({"name": name, "ecosystem": eco, "package": pkg_id})
    return found

def detect_testing_strategies(root: Path, dependencies: dict[str, list[str]]) -> list[str]:
    strategies = []
    py_deps = [d.lower() for d in dependencies.get("python", [])]
    if (root / "pytest.ini").is_file() or any("pytest" in d for d in py_deps):
        strategies.append("pytest")
    elif (root / "tests").is_dir() and any((root / "tests").glob("**/*.py")):
        strategies.append("unittest (python)")

    node_deps = [d.lower() for d in dependencies.get("node", [])]
    if any("jest" in d for d in node_deps) or (root / "jest.config.js").is_file() or (root / "jest.config.ts").is_file():
        strategies.append("jest")
    if any("vitest" in d for d in node_deps) or (root / "vitest.config.ts").is_file() or (root / "vitest.config.js").is_file():
        strategies.append("vitest")

    if (root / "Cargo.toml").is_file():
        strategies.append("cargo test")
    if (root / "go.mod").is_file():
        strategies.append("go test")
    if (root / "phpunit.xml").is_file() or (root / "phpunit.xml.dist").is_file():
        strategies.append("phpunit")

    return strategies

LINTER_PATTERNS = [
    (".eslintrc*", "eslint"),
    ("eslint.config.*", "eslint"),
    (".prettierrc*", "prettier"),
    ("biome.json", "biome"),
    ("ruff.toml", "ruff"),
    (".flake8", "flake8"),
    (".golangci.*", "golangci-lint"),
    ("rustfmt.toml", "rustfmt"),
]

def detect_linters_and_formatters(root: Path) -> list[str]:
    tools = []
    for pat, name in LINTER_PATTERNS:
        if list(root.glob(pat)):
            tools.append(name)
    pyproj = root / "pyproject.toml"
    if pyproj.is_file():
        try:
            txt = pyproj.read_text(encoding="utf-8")
            if "tool.ruff" in txt and "ruff" not in tools:
                tools.append("ruff")
            if "tool.black" in txt and "black" not in tools:
                tools.append("black")
            if "tool.mypy" in txt and "mypy" not in tools:
                tools.append("mypy")
        except Exception as e:
            sys.stderr.write(f"Grounding notice reading pyproject linter config: {e}\n")
    return list(dict.fromkeys(tools))

def detect_ci_cd_and_build(root: Path) -> list[str]:
    configs = []
    if (root / ".github" / "workflows").is_dir() and any((root / ".github" / "workflows").glob("*.yml")):
        configs.append("github-actions")
    if (root / ".gitlab-ci.yml").is_file():
        configs.append("gitlab-ci")
    if (root / "Dockerfile").is_file():
        configs.append("dockerfile")
    if (root / "docker-compose.yml").is_file() or (root / "docker-compose.yaml").is_file():
        configs.append("docker-compose")
    if (root / "Makefile").is_file():
        configs.append("make")
    if (root / "CMakeLists.txt").is_file():
        configs.append("cmake")
    return configs

def detect_project_classification(root: Path, ecosystems: dict[str, list[str]], frameworks: list[dict[str, str]]) -> str:
    if (root / "AGENTS.md").is_file() and (root / ".agents").is_dir() and (root / "scripts" / "verify.py").is_file():
        return "Agent Harness & Tooling Workspace"
    if (root / "pnpm-workspace.yaml").is_file() or (root / "lerna.json").is_file() or (root / "turbo.json").is_file():
        return "Monorepo Workspace"
    if any(f["name"] in ("Next.js", "React", "Vue", "Nuxt", "SvelteKit", "Svelte", "Angular", "Astro") for f in frameworks):
        return "Web Application"
    if any(f["name"] in ("FastAPI", "Express", "Django", "Flask", "NestJS", "Fastify", "Gin", "Echo", "Actix Web", "Axum") for f in frameworks):
        return "Backend API Service"
    if "python" in ecosystems and ((root / "setup.py").is_file() or (root / "pyproject.toml").is_file()):
        return "Python Package / Library"
    if "rust" in ecosystems and (root / "Cargo.toml").is_file():
        return "Rust Crate / Service"
    if "go" in ecosystems and (root / "go.mod").is_file():
        return "Go Module / Service"
    return "Generic / Multi-stack Workspace"

def detect_quality_gates(root: Path) -> list[str]:
    gates = []
    if (root / "scripts" / "verify.py").is_file():
        gates.append("python3 scripts/verify.py --execute --terse")
    pkg_json = root / "package.json"
    if pkg_json.is_file():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            scripts = data.get("scripts") or {}
            for s in ("test", "lint", "typecheck", "build"):
                if s in scripts:
                    gates.append(f"npm run {s}")
        except Exception as e:
            sys.stderr.write(f"Grounding notice reading package.json scripts: {e}\n")
    if (root / "Cargo.toml").is_file():
        gates.append("cargo test")
    if (root / "go.mod").is_file():
        gates.append("go test ./...")
    if (root / "pytest.ini").is_file() or ((root / "tests").is_dir() and any((root / "tests").glob("**/*.py"))):
        if shutil.which("pytest"):
            gates.append("pytest")
        else:
            gates.append('python3 -m unittest discover tests')
    return gates

def ground_workspace(root: Path) -> dict[str, object]:
    ecosystems = detect_ecosystems(root)
    dependencies = extract_dependencies(root, ecosystems)
    layout = inspect_project_layout(root)
    git_state = get_git_state(root)
    environment = detect_environment(root)
    package_managers = detect_package_managers(root)
    frameworks = detect_frameworks(root, dependencies)
    testing = detect_testing_strategies(root, dependencies)
    linters_formatters = detect_linters_and_formatters(root)
    ci_cd = detect_ci_cd_and_build(root)
    project_type = detect_project_classification(root, ecosystems, frameworks)
    quality_gates = detect_quality_gates(root)

    return {
        "root": str(root),
        "ecosystems": ecosystems,
        "dependencies": dependencies,
        "layout": layout,
        "git": git_state,
        "environment": environment,
        "package_managers": package_managers,
        "frameworks": frameworks,
        "testing": testing,
        "testing_strategies": testing,
        "linters_formatters": linters_formatters,
        "ci_cd": ci_cd,
        "project_type": project_type,
        "quality_gates": quality_gates,
    }

def print_grounding_report(data: dict[str, object], json_output: bool = False) -> None:
    if json_output:
        print(json.dumps(data, indent=2))
        return

    env = data.get("environment", {})
    git = data.get("git", {})
    ecosystems = data.get("ecosystems", {})
    pms = data.get("package_managers", {})
    frameworks = data.get("frameworks", [])
    testing = data.get("testing", [])
    linters = data.get("linters_formatters", [])
    ci_cd = data.get("ci_cd", [])
    gates = data.get("quality_gates", [])

    print("=" * 60)
    print("📍 AAC Epistemic Grounding (Codebase Truth Baseline)")
    print("=" * 60)
    print(f"Project Root:   {data.get('root')}")
    print(f"Project Type:   {data.get('project_type', 'UNKNOWN / UNVERIFIED')}")
    print(f"Git Branch:     {git.get('branch', 'unknown')} ({git.get('status', 'unknown')})")
    print(f"Environment:    {env.get('os', 'Unknown')} {env.get('release', '')} ({env.get('machine', '')}) | Python {env.get('python', '')} | Shell: {env.get('shell', '')}")

    if ecosystems:
        print("\n🔍 Detected Ecosystems:")
        for eco, files in ecosystems.items():
            print(f"  • {eco.upper():12} -> Confirmed via: {', '.join(files)}")
    else:
        print("\n🔍 Detected Ecosystems: UNKNOWN / UNVERIFIED (Language-Agnostic Workspace)")

    lock_pms = pms.get("lockfile_managed", [])
    avail_pms = pms.get("available_cli", [])
    print("\n⚡ Package Managers & Tooling:")
    print(f"  • Lockfiles:    {', '.join(lock_pms) if lock_pms else 'UNKNOWN / UNVERIFIED (none detected)'}")
    print(f"  • Available:    {', '.join(avail_pms[:10]) if avail_pms else 'UNKNOWN / UNVERIFIED'}")

    if frameworks:
        print("\n🧩 Detected Frameworks:")
        for fw in frameworks:
            print(f"  • {fw['name']:14} (package: {fw['package']})")
    else:
        print("\n🧩 Framework:     UNKNOWN / UNVERIFIED (Standard library / no external framework detected)")

    dependencies = data.get("dependencies", {})
    if dependencies:
        print("\n📦 Existing Dependencies (DO NOT Re-invent or Duplicate):")
        for eco, deps in dependencies.items():
            print(f"  • {eco.upper()}: {', '.join(deps[:15])}")

    print("\n🧪 Testing & Verification:")
    print(f"  • Test Runners: {', '.join(testing) if testing else 'UNKNOWN / UNVERIFIED (none detected)'}")
    if gates:
        print(f"  • Quality Gate: {gates[0]}")

    lint_str = ', '.join(linters) if linters else 'UNKNOWN / UNVERIFIED (none detected)'
    ci_str = ', '.join(ci_cd) if ci_cd else 'UNKNOWN / UNVERIFIED (none detected)'
    print(f"\n🛠️ Linters/CI:    Linters: {lint_str} | CI/Build: {ci_str}")

    layout = data.get("layout", {})
    dirs = layout.get("directories", [])
    if dirs:
        print(f"\n📂 Top-Level Layout: {', '.join(dirs)}")

    print("=" * 60)
    print("💡 MANDATE: Design and code using existing conventions and libraries.")
    print("Never assume unverified APIs, frameworks, or dependencies.")
    print("============================================================")

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="AAC Epistemic Grounding Engine")
    parser.add_argument("path", nargs="?", default=".", help="Target workspace to ground")
    parser.add_argument("--json", action="store_true", help="Output grounding data in raw JSON")
    args = parser.parse_args()

    target_root = Path(args.path).resolve()
    data = ground_workspace(target_root)
    print_grounding_report(data, json_output=args.json)

if __name__ == "__main__":
    main()

