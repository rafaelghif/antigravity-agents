#!/usr/bin/env python3
"""
AAC Epistemic Grounding Engine:
Pre-Action Reality Check to Eliminate Hallucinations.
Inspects the actual workspace to extract detected languages, package managers,
declared dependencies, existing project layouts, and git state before any agent acts.
Supports all major languages: Python, TS/JS, Go, Rust, Java/Kotlin, C#, PHP, Ruby, Dart/Flutter, C/C++, Elixir, Swift.
"""
from __future__ import annotations

import json, os, re, shutil, subprocess, sys
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
                    node_deps.extend(d + dev_d)
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({pkg_file.name}): {e}\n")
        if node_deps:
            deps["node"] = list(dict.fromkeys(node_deps))[:25]

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
                    matches = re.findall(r'["\']([a-zA-Z0-9_-]+)(?:>=|==|~=|[<>]|["\'])', content)
                    py_deps.extend(matches[:15])
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({pyproj.name}): {e}\n")

        if py_deps:
            deps["python"] = list(dict.fromkeys(py_deps))[:25]
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
                    matches = re.findall(r'^\s+([a-zA-Z0-9.\-_/]+)\s+v', content, re.MULTILINE)
                    go_deps.extend(matches)
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({mod_file.name}): {e}\n")
        if go_deps:
            deps["go"] = list(dict.fromkeys(go_deps))[:20]

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
                    matches = re.findall(r'^\s*([a-zA-Z0-9_-]+)\s*=\s*', content, re.MULTILINE)
                    rust_deps.extend([d for d in matches if d not in ("package", "dependencies", "dev-dependencies")])
                except Exception as e:
                    sys.stderr.write(f"Grounding notice ({cargo_file.name}): {e}\n")
        if rust_deps:
            deps["rust"] = list(dict.fromkeys(rust_deps))[:20]

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
            deps["php"] = list(dict.fromkeys(php_deps))[:20]

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

def ground_workspace(root: Path) -> dict[str, object]:
    ecosystems = detect_ecosystems(root)
    dependencies = extract_dependencies(root, ecosystems)
    layout = inspect_project_layout(root)
    git_state = get_git_state(root)

    return {
        "root": str(root),
        "ecosystems": ecosystems,
        "dependencies": dependencies,
        "layout": layout,
        "git": git_state,
    }

def print_grounding_report(data: dict[str, object], json_output: bool = False) -> None:
    if json_output:
        print(json.dumps(data, indent=2))
        return

    print("=" * 60)
    print("📍 AAC Epistemic Grounding (Codebase Truth Baseline)")
    print("=" * 60)
    print(f"Project Root: {data['root']}")
    print(f"Git Branch:   {data['git']['branch']} ({data['git']['status']})")
    
    ecosystems = data.get("ecosystems", {})
    if ecosystems:
        print("\n🔍 Detected Ecosystems:")
        for eco, files in ecosystems.items():
            print(f"  • {eco.upper():12} -> Confirmed via: {', '.join(files)}")
    else:
        print("\n🔍 Detected Ecosystems: Generic / Language-Agnostic Workspace")

    dependencies = data.get("dependencies", {})
    if dependencies:
        print("\n📦 Existing Dependencies (DO NOT Re-invent or Duplicate):")
        for eco, deps in dependencies.items():
            print(f"  • {eco.upper()}: {', '.join(deps[:15])}")

    layout = data.get("layout", {})
    dirs = layout.get("directories", [])
    if dirs:
        print(f"\n📂 Top-Level Layout: {', '.join(dirs)}")

    print("=" * 60)
    print("💡 MANDATE: Design and code using existing conventions and libraries.")
    print("=" * 60)

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
