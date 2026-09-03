#!/usr/bin/env python3
"""
AAC Installer & Upgrade Engine: Cross-Platform Universal Bootstrap for Antigravity Agent Core.
Runs seamlessly on Linux, macOS, and Windows with Zero Platform Lock-in.
Automatically resolves releases, preserves brain context and memory, and validates workspace.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

GITHUB_API_URL = "https://api.github.com/repos/rafaelghif/antigravity-agents/releases/latest"
REMOTE_REPO = "https://github.com/rafaelghif/antigravity-agents.git"
TARBALL_URL_TEMPLATE = "https://github.com/rafaelghif/antigravity-agents/archive/refs/tags/{tag}.tar.gz"

BRAIN_PRESERVE_FILES = (
    "rules.md",
    "memory.md",
    "ANCHOR.md",
    "active_context.md",
    "soul.md",
    "schema.md",
    "AITL_CONSENSUS.yaml",
    "env-required.json",
)


def parse_semver(v_str: str) -> tuple[int, int, int]:
    clean = re.sub(r"^[^\d]*", "", v_str)
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", clean)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return (0, 0, 0)


def is_newer_version(latest_str: str, current_str: str) -> bool:
    return parse_semver(latest_str) > parse_semver(current_str)


def get_current_version(root_dir: Path) -> str:
    config_path = root_dir / ".agents" / "config.json"
    if config_path.is_file():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return data.get("core_version", "0.0.0")
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"Config read notice: {exc}\n")
    return "0.0.0"


def get_latest_github_release(current_ver: str) -> tuple[str, str, str]:
    # 1. Primary: Standard library urllib
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": "AAC-Installer", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
            data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            title = data.get("name", tag)
            body = data.get("body", "")
            if tag:
                return (tag, title, body)
    except Exception as exc:
        sys.stderr.write(f"GitHub API release notice (urllib): {exc}\n")

    # 2. Fallback: Git ls-remote
    try:
        res = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", REMOTE_REPO],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
        )
        if res.returncode == 0:
            tags = [line.split("/")[-1] for line in res.stdout.splitlines() if line.strip()]
            valid_tags = [t for t in tags if re.match(r"^v?\d+\.\d+\.\d+$", t)]
            if valid_tags:
                sorted_tags = sorted(valid_tags, key=parse_semver)
                latest_tag = sorted_tags[-1]
                return (latest_tag, latest_tag, "Upstream release from Git tags.")
    except Exception as exc:
        sys.stderr.write(f"Git remote tags notice: {exc}\n")

    fallback_tag = f"v{current_ver}" if current_ver != "0.0.0" else "v4.43.0"
    return (fallback_tag, fallback_tag, "Fallback version.")


def check_update_status(root_dir: Path) -> dict[str, object]:
    current = get_current_version(root_dir)
    latest_tag, title, notes = get_latest_github_release(current)
    has_update = is_newer_version(latest_tag, current)
    return {
        "current_version": current,
        "latest_version": latest_tag,
        "title": title,
        "notes": notes,
        "has_update": has_update,
    }


def copy_managed_item(src: Path, dst: Path, backup_dir: Path) -> None:
    """Safely backs up existing target item before copying managed source item."""
    if dst.exists():
        rel = dst.name
        backup_dst = backup_dir / rel
        if dst.is_dir():
            shutil.copytree(dst, backup_dst, dirs_exist_ok=True)
        else:
            backup_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup_dst)

    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def install_aac(root_dir: Path, target_version: str) -> bool:
    print(f"\n=> Installing Antigravity Agent Core ({target_version}) to: {root_dir}")
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = root_dir / ".agents-backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Preserve existing custom brain context
    preserved_brain: dict[str, str] = {}
    brain_dir = root_dir / ".agents" / "brain"
    if brain_dir.is_dir():
        for bf in BRAIN_PRESERVE_FILES:
            target_bf = brain_dir / bf
            if target_bf.is_file():
                try:
                    preserved_brain[bf] = target_bf.read_text(encoding="utf-8")
                except Exception as e:
                    sys.stderr.write(f"Notice reading {bf}: {e}\n")

    # 2. Acquire release source in a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        source_dir = tmp_dir / "source"
        
        cloned = False
        # Try git clone first
        if shutil.which("git"):
            try:
                res = subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", target_version, REMOTE_REPO, str(source_dir)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                )
                cloned = res.returncode == 0
            except Exception as e:
                sys.stderr.write(f"Git clone notice: {e}\n")

        # Fallback to downloading tarball via urllib
        if not cloned or not source_dir.exists():
            tarball_url = TARBALL_URL_TEMPLATE.format(tag=target_version)
            tar_path = tmp_dir / "release.tar.gz"
            try:
                req = urllib.request.Request(tarball_url, headers={"User-Agent": "AAC-Installer"})
                with urllib.request.urlopen(req, timeout=20) as resp, open(tar_path, "wb") as out_f:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
                    shutil.copyfileobj(resp, out_f)
                
                import tarfile
                with tarfile.open(tar_path, "r:gz") as tar:
                    if hasattr(tarfile, 'data_filter'):
                        tar.extractall(path=tmp_dir, filter='data')  # nosemgrep: trailofbits.python.tarfile-extractall-traversal.tarfile-extractall-traversal
                    else:
                        tar.extractall(path=tmp_dir)  # nosemgrep: trailofbits.python.tarfile-extractall-traversal.tarfile-extractall-traversal
                extracted_dirs = [d for d in tmp_dir.iterdir() if d.is_dir() and d != source_dir]
                if extracted_dirs:
                    source_dir = extracted_dirs[0]
                    cloned = True
            except Exception as e:
                sys.stderr.write(f"Tarball download notice: {e}\n")

        if not cloned or not source_dir.exists():
            print("=> ERROR: Unable to acquire release sources from GitHub.")
            return False

        # 3. Validate source structure
        validate_script = source_dir / "scripts" / "validate.py"
        if validate_script.is_file():
            val_res = subprocess.run([sys.executable, str(validate_script)], cwd=source_dir)
            if val_res.returncode != 0:
                print("=> ERROR: Source validation failed. Aborting installation.")
                return False

        # 4. Copy managed files to target workspace
        (root_dir / ".agents" / "scratch").mkdir(parents=True, exist_ok=True)
        (root_dir / "tasks").mkdir(parents=True, exist_ok=True)
        (root_dir / "scripts").mkdir(parents=True, exist_ok=True)

        copy_managed_item(source_dir / "AGENTS.md", root_dir / "AGENTS.md", backup_dir)
        copy_managed_item(source_dir / "GEMINI.md", root_dir / "GEMINI.md", backup_dir)
        copy_managed_item(source_dir / ".agents", root_dir / ".agents", backup_dir)
        copy_managed_item(source_dir / "scripts", root_dir / "scripts", backup_dir)
        
        if (source_dir / ".githooks").is_dir():
            copy_managed_item(source_dir / ".githooks", root_dir / ".githooks", backup_dir)

        env_example_src = source_dir / ".env.example"
        env_example_dst = root_dir / ".env.example"
        if env_example_src.is_file() and not env_example_dst.exists():
            shutil.copy2(env_example_src, env_example_dst)

        # 5. Restore preserved brain files
        for bf, content in preserved_brain.items():
            bf_path = root_dir / ".agents" / "brain" / bf
            bf_path.parent.mkdir(parents=True, exist_ok=True)
            bf_path.write_text(content, encoding="utf-8")

        # 6. Ensure .gitignore has scratch rule
        gitignore_path = root_dir / ".gitignore"
        try:
            if gitignore_path.is_file():
                gi_text = gitignore_path.read_text(encoding="utf-8")
                if ".agents/scratch/" not in gi_text:
                    gitignore_path.write_text(gi_text.rstrip() + "\n\n# Antigravity Scratch Directory\n.agents/scratch/\n", encoding="utf-8")
            else:
                gitignore_path.write_text("# Antigravity Scratch Directory\n.agents/scratch/\n", encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Gitignore update notice: {e}\n")

        # 7. Configure Git Hooks safely if .git exists
        if (root_dir / ".git").is_dir() and (root_dir / ".githooks" / "pre-commit").is_file():
            try:
                hooks_res = subprocess.run(
                    ["git", "config", "core.hooksPath"],
                    cwd=root_dir,
                    capture_output=True,
                    text=True
                )
                current_hooks = hooks_res.stdout.strip()
                if not current_hooks or current_hooks == ".githooks":
                    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=root_dir, check=True)
                    print("=> L9 Git Hooks configured (.githooks).")
            except Exception as e:
                sys.stderr.write(f"Git hook setup notice: {e}\n")

        # 8. Clean up accidental workflow directories in target project
        wf_dir = root_dir / ".github" / "workflows"
        if wf_dir.is_dir():
            for f in ("agent-gates.yml", "agentic-cicd.yml"):
                wf_file = wf_dir / f
                if wf_file.is_file():
                    wf_file.unlink()
            try:
                wf_dir.rmdir()
                (root_dir / ".github").rmdir()
            except OSError as err:
                sys.stderr.write(f"Notice: .github cleanup: {err}\n")

        return True


def run_upgrade(root_dir: Path, target_version: str) -> bool:
    """Delegates to native cross-platform installation."""
    return install_aac(root_dir, target_version)


def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Installer Engine: Auto-bootstrap the world-class L9 agent workspace")
    parser.add_argument("path", nargs="?", default=".", help="Project workspace root")
    parser.add_argument("--check", action="store_true", help="Check for latest version without installing")
    parser.add_argument("--force", action="store_true", help="Force re-installation")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    status = check_update_status(root_dir)

    print("=" * 60)
    print("🚀 Antigravity Agent Core (AAC) Installer")
    print("=" * 60)
    print(f"Current Workspace Version: v{status['current_version']}")
    print(f"Latest Upstream Release:   {status['latest_version']}")

    if not status["has_update"] and not args.force and status["current_version"] != "0.0.0":
        print("\n✨ You are already running the latest world-class AAC agent!")
        return

    if status["has_update"] or status["current_version"] == "0.0.0":
        action = "Update" if status["current_version"] != "0.0.0" else "Install"
        print(f"\n🎉 Latest {action} Available: {status['latest_version']} ({status['title']})")
        print("\n--- Release Notes Highlight ---")
        first_lines = "\n".join(str(status["notes"]).splitlines()[:10])
        print(first_lines)
        print("-------------------------------")

    if args.check:
        print("\nRun 'python3 install.py' to apply this configuration effortlessly.")
        return

    success = install_aac(root_dir, str(status["latest_version"]))
    if success:
        print("\n" + "=" * 60)
        print(f"✅ AAC successfully configured to {status['latest_version']}!")
        print("💡 All custom memories (.agents/brain/memory.md) and rules were preserved.")
        print("=" * 60)
        verify_script = root_dir / "scripts" / "verify.py"
        if verify_script.is_file():
            print("\n=> Running post-install verification gates...")
            subprocess.run([sys.executable, str(verify_script), "--execute", "--terse"], cwd=root_dir)
    else:
        print("\n❌ Installation failed. Check logs above or rollback with .agents-backups/.")
        sys.exit(1)


if __name__ == "__main__":
    main()

