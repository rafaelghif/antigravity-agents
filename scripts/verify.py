#!/usr/bin/env python3
"""Detect a repository stack and print or execute safe verification commands."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import shlex
import sys
import os
from pathlib import Path

try:
    from scripts import platform_guard  # noqa: F401
except ImportError:
    import platform_guard  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]


def split_cmd(cmd_str: str) -> list[str]:
    is_windows = sys.platform == "win32"
    parts = shlex.split(cmd_str, posix=not is_windows)
    if is_windows:
        parts = [p.strip('"') for p in parts]
    return parts


def command(*parts: str) -> str:
    return " ".join(parts)


def detect(target_root: Path | None = None) -> list[tuple[str, str, str]]:
    root = target_root or ROOT
    checks: list[tuple[str, str, str]] = []
    if (root / "package.json").is_file():
        try:
            data = json.loads((root / "package.json").read_text(encoding="utf-8"))
            scripts = data.get("scripts") or {}
        except (json.JSONDecodeError, AttributeError, TypeError):
            scripts = {}
        manager = "npm"
        if (root / "pnpm-lock.yaml").is_file():
            manager = "pnpm"
        elif (root / "yarn.lock").is_file():
            manager = "yarn"
        elif (root / "bun.lockb").is_file() or (root / "bun.lock").is_file():
            manager = "bun"
        pm = data.get("packageManager", "")
        if pm:
            clean_pm = pm.split("@")[0].strip()
            if clean_pm in ("pnpm", "yarn", "npm", "bun"):
                manager = clean_pm

        for name in ("format", "lint", "typecheck", "test", "build"):
            if name in scripts:
                checks.append((name, manager, command(manager, "run", name)))
    elif not (root / "package.json").is_file():
        for sub in ("frontend", "client", "web", "apps/web", "packages/web"):
            sub_pkg = root / sub / "package.json"
            if sub_pkg.is_file():
                try:
                    sub_data = json.loads(sub_pkg.read_text(encoding="utf-8"))
                    sub_scripts = sub_data.get("scripts") or {}
                except Exception:
                    sub_scripts = {}
                if "test" in sub_scripts:
                    sub_pm = "npm"
                    if (root / sub / "pnpm-lock.yaml").is_file() or (root / "pnpm-lock.yaml").is_file():
                        sub_pm = "pnpm"
                    elif (root / sub / "yarn.lock").is_file() or (root / "yarn.lock").is_file():
                        sub_pm = "yarn"
                    elif (root / sub / "bun.lockb").is_file() or (root / sub / "bun.lock").is_file() or (root / "bun.lockb").is_file():
                        sub_pm = "bun"
                    checks.append(("test", "node", f"{sub_pm} --prefix {sub} test" if sub_pm == "npm" else f"{sub_pm} run --prefix {sub} test"))
                    break

    if (root / "pyproject.toml").is_file() or (root / "pytest.ini").is_file():
        if shutil.which("pytest"):
            checks.append(("test", "python", "pytest"))
        elif (root / "tests").is_dir() and any((root / "tests").glob("**/*.py")):
            checks.append(("test", "python", f'"{sys.executable}" -m unittest discover tests'))
    elif (root / "tests").is_dir() and any((root / "tests").glob("**/*.py")):
        checks.append(("test", "python", f'"{sys.executable}" -m unittest discover tests'))
    else:
        for sub in ("backend", "server", "api", "app"):
            sub_tests = root / sub / "tests"
            if sub_tests.is_dir() and any(sub_tests.glob("**/*.py")):
                checks.append(("test", "python", f'"{sys.executable}" -m unittest discover {sub}/tests'))
                break
    if (root / "Cargo.toml").is_file():
        checks.append(("test", "rust", "cargo test"))
    if (root / "go.mod").is_file():
        checks.append(("test", "go", "go test ./..."))
    if (root / "composer.json").is_file():
        checks.append(("test", "php", "composer test"))
    # Java & Kotlin (Maven / Gradle)
    if (root / "pom.xml").is_file():
        mvn = "./mvnw" if (root / "mvnw").is_file() else "mvn"
        checks.append(("test", "java", f"{mvn} test"))
    if (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        gradle = "./gradlew" if (root / "gradlew").is_file() else "gradle"
        checks.append(("test", "java", f"{gradle} test"))
    # .NET / C#
    if list(root.glob("*.csproj")) or list(root.glob("*.sln")):
        checks.append(("test", "dotnet", "dotnet test"))
    # C / C++
    if (root / "CMakeLists.txt").is_file():
        checks.append(("test", "cpp", "ctest --output-on-failure"))
    elif (root / "Makefile").is_file():
        checks.append(("test", "make", "make test"))
    # Ruby
    if (root / "Gemfile").is_file():
        checks.append(("test", "ruby", "bundle exec rspec" if shutil.which("rspec") else "rake test"))
    # Dart / Flutter
    if (root / "pubspec.yaml").is_file():
        runner = "flutter test" if shutil.which("flutter") else "dart test"
        checks.append(("test", "dart", runner))
    # Elixir
    if (root / "mix.exs").is_file():
        checks.append(("test", "elixir", "mix test"))
    # Swift
    if (root / "Package.swift").is_file():
        checks.append(("test", "swift", "swift test"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect a repository stack and print or execute safe verification commands.")
    parser.add_argument("path", nargs="?", default=None, help="Target workspace root")
    parser.add_argument("--path", dest="target_path", default=None, help="Target workspace root")
    parser.add_argument("--execute", action="store_true", help="Execute the detected commands")
    parser.add_argument("--terse", "-q", action="store_true", help="ACI Mode: output minimal telegraphic summary")
    parser.add_argument("--release", action="store_true", help="Enforce production release gate: requires .agents/brain/AITL_CONSENSUS.yaml approval")
    args = parser.parse_args()

    target_root = Path(args.target_path or args.path).resolve() if (args.target_path or args.path) else ROOT

    if args.release:
        aitl_file = target_root / ".agents" / "brain" / "AITL_CONSENSUS.yaml"
        if not aitl_file.is_file():
            print("=> FATAL: Production release gate failed! .agents/brain/AITL_CONSENSUS.yaml is missing.")
            return 1
        try:
            aitl_text = aitl_file.read_text(encoding="utf-8")
            if "STATUS: APPROVED" not in aitl_text:
                print("=> FATAL: Production release gate failed! AITL_CONSENSUS.yaml does not have STATUS: APPROVED.")
                return 1
            if not args.terse:
                print("✅ AITL Consensus Verified (.agents/brain/AITL_CONSENSUS.yaml: APPROVED)")
        except Exception as e:
            print(f"=> FATAL: Error reading AITL_CONSENSUS.yaml: {e}")
            return 1

    # L9 Hard Boundaries for Agent Compliance are now handled by intent_guard.py
    checks = detect(target_root)
    
    script_checks = [
        ("intent_guard.py", "intent_lifecycle_check", "", True),
        ("validate.py", "validate", "", False),
        ("complexity_analyzer.py", "complexity_check", "", False),
        ("test_quality_guard.py", "anti_sham_check", "", False),
        ("dry_guard.py", "dry_check", "--check", False),
        ("git_hygiene_guard.py", "git_hygiene_check", "--check", False),
        ("ui_hygiene_guard.py", "ui_hygiene_check", "--check", False),
    ]

    for script, check_name, extra_args, at_start in script_checks:
        script_path = target_root / "scripts" / script
        if script_path.is_file():
            cmd = f'"{sys.executable}" scripts/{script}'
            if extra_args:
                cmd += f" {extra_args}"
            item = (check_name, "AAC", cmd)
            if at_start:
                checks.insert(0, item)
            else:
                checks.append(item)

    neuro_engine = target_root / "scripts" / "neurosymbolic_engine.py"
    if neuro_engine.is_file():
        handoff_file = target_root / "handoff.json"
        if not handoff_file.is_file():
            baseline_handoff = {
                "task_id": "INIT",
                "worker_role": "scrum-master",
                "summary": f"Initialized AAC workspace for {target_root.name}",
                "modifications": [],
                "tests": [],
                "confidence_score": 1.0,
                "requires_human": False
            }
            handoff_file.write_text(json.dumps(baseline_handoff, indent=2), encoding="utf-8")
            if not args.terse:
                print("💡 Initialized default handoff.json for workspace.")
        checks.append(("neurosymbolic_validation", "AAC", f'"{sys.executable}" scripts/neurosymbolic_engine.py handoff.json'))
        
    if not checks:
        if args.terse:
            print("=> ACI VERIFY: NOT VERIFIED (No application stack test runner or quality gates detected).")
        else:
            print("- application stack: not detected (NOT VERIFIED)")
            print("- project tests/formatters/linters: not available")
        return 0

    if not args.terse:
        print("Stack detection:")
        for name, stack, run in checks:
            status = "available" if shutil.which(split_cmd(run)[0]) else "not available"
            print(f"- {stack} {name}: {run} ({status})")

    exit_code = 0
    passed_count = 0
    executable_count = 0
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    for name, stack, run in checks:
        status = "available" if shutil.which(split_cmd(run)[0]) else "not available"
        if status == "available":
            executable_count += 1
        if args.execute and status == "available":
            if not args.terse:
                print(f"\n=> Executing {stack} {name}...")
                result = subprocess.run(split_cmd(run), cwd=target_root, timeout=300, env=sub_env)
            else:
                result = subprocess.run(
                    split_cmd(run),
                    cwd=target_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=sub_env,
                    timeout=300
                )
            
            if result.returncode != 0:
                print(f"=> ERROR: {stack} {name} failed with exit code {result.returncode}")
                if args.terse and result.stderr:
                    print(result.stderr.strip())
                elif args.terse and result.stdout:
                    print(result.stdout.strip())
                exit_code = result.returncode
            else:
                passed_count += 1
                if not args.terse:
                    print(f"=> SUCCESS: {stack} {name} passed.")

    if not args.execute:
        if args.terse:
            print(f"=> ACI VERIFY: DRY-RUN ({len(checks)} gates detected, 0 executed. Run with --execute).")
        return 0

    if args.terse:
        if exit_code != 0:
            pass
        elif executable_count == 0 and len(checks) > 0:
            print(f"=> ACI VERIFY: NOT VERIFIED (0/{len(checks)} gates executed: required tools not available).")
            return 1
        elif passed_count < len(checks):
            print(f"=> ACI VERIFY: PARTIAL ({passed_count}/{len(checks)} gates passed, {len(checks) - passed_count} skipped - tools not available).")
        else:
            print(f"=> ACI VERIFY: OK ({passed_count}/{len(checks)} gates passed).")
    else:
        if exit_code == 0:
            if executable_count == 0 and len(checks) > 0:
                print(f"\n=> ACI VERIFY: NOT VERIFIED (0/{len(checks)} gates executed: required tools not available).")
                return 1
            elif passed_count < len(checks):
                print(f"\n=> ACI VERIFY: PARTIAL ({passed_count}/{len(checks)} gates passed, {len(checks) - passed_count} skipped - tools not available).")
            else:
                print(f"\n=> ACI VERIFY: OK ({passed_count}/{len(checks)} gates passed).")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
