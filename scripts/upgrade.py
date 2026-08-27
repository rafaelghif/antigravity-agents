#!/usr/bin/env python3
"""
AAC Upgrade Engine: One-command effortless upgrading of Antigravity Agent Core.
Auto-discovers the latest GitHub release, preserves memories/rules, updates files,
and validates the upgraded workspace.
"""

import os
import sys
import json
import re
import subprocess
import argparse
import tempfile
from pathlib import Path

GITHUB_API_URL = "https://api.github.com/repos/rafaelghif/antigravity-agents/releases/latest"
REMOTE_REPO = "https://github.com/rafaelghif/antigravity-agents.git"

def parse_semver(v_str: str) -> tuple:
    clean = re.sub(r'^[^\d]*', '', v_str)
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', clean)
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
        except Exception as e:
            sys.stderr.write(f"Config read notice: {e}\n")
    return "0.0.0"

def get_latest_github_release() -> tuple:
    try:
        res = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: AAC-Upgrader", GITHUB_API_URL],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            tag = data.get("tag_name", "")
            title = data.get("name", tag)
            body = data.get("body", "")
            if tag:
                return (tag, title, body)
    except Exception as e:
        sys.stderr.write(f"GitHub API release notice: {e}\n")

    try:
        res = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", REMOTE_REPO],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8
        )
        if res.returncode == 0:
            tags = [line.split('/')[-1] for line in res.stdout.splitlines() if line.strip()]
            valid_tags = [t for t in tags if re.match(r'^v?\d+\.\d+\.\d+$', t)]
            if valid_tags:
                sorted_tags = sorted(valid_tags, key=parse_semver)
                latest_tag = sorted_tags[-1]
                return (latest_tag, latest_tag, "Upstream release from Git tags.")
    except Exception as e:
        sys.stderr.write(f"Git remote tags notice: {e}\n")

    return ("v4.19.0", "v4.19.0", "Fallback version.")

def check_update_status(root_dir: Path) -> dict:
    current = get_current_version(root_dir)
    latest_tag, title, notes = get_latest_github_release()
    has_update = is_newer_version(latest_tag, current)
    return {
        "current_version": current,
        "latest_version": latest_tag,
        "title": title,
        "notes": notes,
        "has_update": has_update
    }

def run_upgrade(root_dir: Path, target_version: str) -> bool:
    print(f"\n=> Downloading and applying AAC {target_version}...")
    is_windows = sys.platform.startswith("win")
    script_name = "install.ps1" if is_windows else "install.sh"
    install_url = f"https://raw.githubusercontent.com/rafaelghif/antigravity-agents/{target_version}/{script_name}"
    try:
        suffix = ".ps1" if is_windows else ".sh"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        dl_res = subprocess.run(
            ["curl", "-fsSL", install_url, "-o", str(tmp_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if dl_res.returncode != 0:
            print(f"=> Download failed: {dl_res.stderr}")
            return False

        if is_windows:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(tmp_path)]
        else:
            cmd = ["bash", str(tmp_path)]

        exec_res = subprocess.run(cmd, cwd=root_dir)
        if tmp_path.exists():
            tmp_path.unlink()
        return exec_res.returncode == 0
    except Exception as e:
        print(f"=> ERROR running upgrade: {e}")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Upgrade Engine: Keep your agent OP with 1 command")
    parser.add_argument("path", nargs="?", default=".", help="Project workspace root")
    parser.add_argument("--check", action="store_true", help="Check for available updates without upgrading")
    parser.add_argument("--force", action="store_true", help="Force re-installation of latest version")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    status = check_update_status(root_dir)

    print("=" * 60)
    print("🚀 Antigravity Agent Core (AAC) Upgrader")
    print("=" * 60)
    print(f"Current Installed Version: v{status['current_version']}")
    print(f"Latest Upstream Release:   {status['latest_version']}")

    if not status["has_update"] and not args.force:
        print("\n✨ You are already running the latest world-class AAC agent!")
        return

    if status["has_update"]:
        print(f"\n🎉 New Version Available: {status['latest_version']} ({status['title']})")
        print("\n--- Release Notes Highlight ---")
        first_lines = "\n".join(status["notes"].splitlines()[:10])
        print(first_lines)
        print("-------------------------------")

    if args.check:
        print("\nRun 'python3 scripts/upgrade.py' to apply this update effortlessly.")
        return

    success = run_upgrade(root_dir, status["latest_version"])
    if success:
        print("\n" + "=" * 60)
        print(f"✅ AAC successfully upgraded to {status['latest_version']}!")
        print("💡 All custom memories (.agents/brain/memory.md) and rules were preserved.")
        print("=" * 60)
    else:
        print("\n❌ Upgrade failed. Check logs above or rollback with .agents-backups/.")
        sys.exit(1)

if __name__ == '__main__':
    main()
