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

def _find_eco_manifests(root: Path, patterns: list[str]) -> list[str]:
    found = []
    for pat in patterns:
        if "*" in pat:
            matches = list(root.glob(pat))
            found.extend(m.name for m in matches)
        elif (root / pat).is_file():
            found.append(pat)
    return found

def detect_ecosystems(root: Path) -> dict[str, list[str]]:
    detected = {}
    for eco, patterns in MANIFEST_CONFIGS.items():
        found = _find_eco_manifests(root, patterns)
        if found:
            detected[eco] = found
    return detected

def extract_dependencies(root: Path, ecosystems: dict[str, list[str]]) -> dict[str, list[str]]:
    deps = {}
    
    # Node
    if "node" in ecosystems and (root / "package.json").is_file():
        try:
            pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
            d = list((pkg.get("dependencies") or {}).keys())
            dev_d = list((pkg.get("devDependencies") or {}).keys())
            deps["node"] = (d + dev_d)[:25]
        except Exception as e:
            sys.stderr.write(f"Grounding notice (package.json): {e}\n")

    # Python
    if "python" in ecosystems:
        py_deps = []
        req_txt = root / "requirements.txt"
        if req_txt.is_file():
            try:
                for line in req_txt.read_text(encoding="utf-8").splitlines():
                    clean = line.strip().split("#")[0].split("==")[0].split(">=")[0].strip()
                    if clean and not clean.startswith("-"):
                        py_deps.append(clean)
            except Exception as e:
                sys.stderr.write(f"Grounding notice (requirements.txt): {e}\n")
        pyproj = root / "pyproject.toml"
        if pyproj.is_file():
            try:
                content = pyproj.read_text(encoding="utf-8")
                matches = re.findall(r'["\']([a-zA-Z0-9_-]+)(?:>=|==|~=|[<>]|["\'])', content)
                py_deps.extend(matches[:15])
            except Exception as e:
                sys.stderr.write(f"Grounding notice (pyproject.toml): {e}\n")
        if py_deps:
            deps["python"] = list(dict.fromkeys(py_deps))[:25]

    # Go
    if "go" in ecosystems and (root / "go.mod").is_file():
        try:
            content = (root / "go.mod").read_text(encoding="utf-8")
            go_deps = re.findall(r'^\s+([a-zA-Z0-9.\-_/]+)\s+v', content, re.MULTILINE)
            if go_deps:
                deps["go"] = go_deps[:20]
        except Exception as e:
            sys.stderr.write(f"Grounding notice (go.mod): {e}\n")

    # Rust
    if "rust" in ecosystems and (root / "Cargo.toml").is_file():
        try:
            content = (root / "Cargo.toml").read_text(encoding="utf-8")
            rust_deps = re.findall(r'^\s*([a-zA-Z0-9_-]+)\s*=\s*', content, re.MULTILINE)
            if rust_deps:
                deps["rust"] = [d for d in rust_deps if d not in ("package", "dependencies", "dev-dependencies")][:20]
        except Exception as e:
            sys.stderr.write(f"Grounding notice (Cargo.toml): {e}\n")

    # PHP
    if "php" in ecosystems and (root / "composer.json").is_file():
        try:
            data = json.loads((root / "composer.json").read_text(encoding="utf-8"))
            reqs = list((data.get("require") or {}).keys())
            deps["php"] = reqs[:20]
        except Exception as e:
            sys.stderr.write(f"Grounding notice (composer.json): {e}\n")

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
            res_b = subprocess.run(["git", "branch", "--show-current"], cwd=root, capture_output=True, text=True)
            if res_b.returncode == 0 and res_b.stdout.strip():
                state["branch"] = res_b.stdout.strip()
            res_s = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
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
