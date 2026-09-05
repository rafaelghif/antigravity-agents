#!/usr/bin/env python3
"""
AAC Installer & Upgrade Engine: Cross-Platform Universal Bootstrap for Antigravity Agent Core.
Runs seamlessly on Linux, macOS, and Windows with Zero Platform Lock-in.
Automatically resolves releases, preserves brain context and memory, and validates workspace.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    from scripts import platform_guard  # noqa: F401
except ImportError:
    for _s in (sys.stdout, sys.stderr):
        if _s and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(encoding="utf-8", errors="replace")
            except Exception as _err:
                sys.stderr.write(f"Stdio notice: {_err}\n")

GITHUB_API_URL = "https://api.github.com/repos/rafaelghif/antigravity-agents/releases/latest"
REMOTE_REPO = "https://github.com/rafaelghif/antigravity-agents.git"
TARBALL_URL_TEMPLATE = "https://github.com/rafaelghif/antigravity-agents/archive/refs/tags/{tag}.tar.gz"

BRAIN_PRESERVE_FILES = (
    "rules.md",
    "memory.md",
    "ANCHOR.md",
    "active_context.md",
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

    fallback_tag = f"v{current_ver}" if current_ver != "0.0.0" else "v4.45.0"
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


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_installation(root_dir: Path) -> dict[str, object]:
    manifest_path = root_dir / ".agents" / "install_manifest.json"
    current_version = get_current_version(root_dir)
    source_repo = REMOTE_REPO
    source_rev = f"v{current_version}"
    installed_at = "UNKNOWN"
    managed_files: dict[str, str] = {}

    if manifest_path.is_file():
        try:
            mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
            current_version = mdata.get("installed_version", current_version)
            source_repo = mdata.get("source_repository", source_repo)
            source_rev = mdata.get("source_revision", source_rev)
            installed_at = mdata.get("install_timestamp", "UNKNOWN")
            managed_files = mdata.get("managed_files", {})
        except Exception as exc:
            sys.stderr.write(f"Manifest read notice: {exc}\n")

    modified_files = []
    missing_files = []
    intact_files = []

    for rel_path_str, expected_hash in managed_files.items():
        file_path = root_dir / rel_path_str
        if not file_path.exists():
            missing_files.append(rel_path_str)
        else:
            try:
                curr_hash = compute_sha256(file_path)
                if curr_hash != expected_hash:
                    modified_files.append(rel_path_str)
                else:
                    intact_files.append(rel_path_str)
            except Exception:
                modified_files.append(rel_path_str)

    status_str = "INTACT" if (not modified_files and not missing_files and managed_files) else ("UNVERIFIED" if not managed_files else "COMPROMISED")

    return {
        "installed_version": current_version,
        "source_repository": source_repo,
        "source_revision": source_rev,
        "install_timestamp": installed_at,
        "total_managed_files": len(managed_files),
        "intact_files": intact_files,
        "modified_files": modified_files,
        "missing_files": missing_files,
        "integrity_status": status_str,
    }


def run_repair(root_dir: Path, source_override: Path | None = None) -> bool:
    print(f"\n=> Running AAC Workspace Self-Repair for: {root_dir}")
    audit = audit_installation(root_dir)
    target_version = str(audit["source_revision"])
    if not target_version or target_version == "UNKNOWN" or target_version == "v0.0.0":
        target_version = f"v{get_current_version(root_dir)}"
    if target_version == "v0.0.0":
        target_version = "v4.45.0"
    print(f"Targeting repair version: {target_version}")
    success = install_aac(root_dir, target_version, source_override=source_override)
    if success:
        print("✅ Repair complete. Managed files restored.")
    return success


def run_rollback(root_dir: Path, target_backup: str | None = None) -> bool:
    backups_dir = root_dir / ".agents-backups"
    if not backups_dir.is_dir():
        print("=> ERROR: No .agents-backups/ directory found. Cannot rollback.")
        return False

    available_backups = sorted([d for d in backups_dir.iterdir() if d.is_dir()], key=lambda d: d.name, reverse=True)
    if not available_backups:
        print("=> ERROR: No previous backup snapshots found in .agents-backups/.")
        return False

    selected_backup = None
    if target_backup:
        for b in available_backups:
            if b.name == target_backup:
                selected_backup = b
                break
        if not selected_backup:
            print(f"=> ERROR: Specified backup '{target_backup}' not found in .agents-backups/.")
            return False
    else:
        selected_backup = available_backups[0]

    print(f"\n=> Rolling back AAC workspace using snapshot: {selected_backup.name}")
    for item in selected_backup.iterdir():
        dst = root_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst)
    print(f"✅ Rollback successful. Restored state from {selected_backup.name}.")
    return True


def run_uninstall(root_dir: Path) -> bool:
    print(f"\n=> Initiating Safe AAC Uninstallation from: {root_dir}")
    manifest_path = root_dir / ".agents" / "install_manifest.json"

    # 1. Archive brain context before removal so user memories are never lost
    brain_dir = root_dir / ".agents" / "brain"
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if brain_dir.is_dir():
        backup_archive = root_dir / ".agents-backups" / f"uninstall_{timestamp}_brain"
        backup_archive.mkdir(parents=True, exist_ok=True)
        shutil.copytree(brain_dir, backup_archive / "brain", dirs_exist_ok=True)
        print(f"💡 User brain context archived to: {backup_archive}")

    # 2. Read managed files from manifest
    files_to_remove: list[Path] = []
    if manifest_path.is_file():
        try:
            mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
            for rel in mdata.get("managed_files", {}):
                files_to_remove.append(root_dir / rel)
        except Exception as exc:
            _ = exc

    if not files_to_remove:
        files_to_remove.extend([
            root_dir / "AGENTS.md",
            root_dir / "GEMINI.md",
            root_dir / "agent.md",
        ])
        if (root_dir / "scripts").is_dir():
            files_to_remove.extend(list((root_dir / "scripts").rglob("*.py")))
        if (root_dir / ".agents").is_dir():
            files_to_remove.extend([p for p in (root_dir / ".agents").rglob("*") if "brain" not in p.parts])

    # 3. Remove files safely
    removed_count = 0
    for p in files_to_remove:
        try:
            if p.is_file():
                p.unlink()
                removed_count += 1
        except OSError as exc:
            _ = exc

    # Clean directories if empty
    for d in (root_dir / ".agents" / "scratch", root_dir / ".agents" / "plugins", root_dir / ".agents" / "skills", root_dir / ".agents" / "agents", root_dir / ".agents" / "rules", root_dir / "scripts"):
        if d.is_dir():
            try:
                shutil.rmtree(d)
            except OSError as exc:
                _ = exc

    # 4. Reset git hooks if configured
    if (root_dir / ".git").is_dir():
        try:
            hooks_res = subprocess.run(["git", "config", "core.hooksPath"], cwd=root_dir, capture_output=True, text=True)
            if hooks_res.stdout.strip() == ".githooks":
                subprocess.run(["git", "config", "--unset", "core.hooksPath"], cwd=root_dir)
                print("=> Git core.hooksPath unset.")
        except Exception as exc:
            _ = exc

    # 5. Clean .gitignore entries
    gi_path = root_dir / ".gitignore"
    if gi_path.is_file():
        try:
            gi_text = gi_path.read_text(encoding="utf-8")
            gi_text = re.sub(r"\n*# Antigravity Managed Directories\n\.agents/scratch/\n\.agents-backups/\n*", "\n", gi_text)
            gi_path.write_text(gi_text.strip() + "\n", encoding="utf-8")
        except Exception as exc:
            _ = exc

    print(f"✅ Uninstallation complete. Removed {removed_count} managed files.")
    return True


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


def scan_managed_dir(dir_path: Path, root_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for sub_file in dir_path.rglob("*"):
        if sub_file.is_file():
            rel = str(sub_file.relative_to(root_dir)).replace("\\", "/")
            if "brain" in sub_file.parts or "scratch" in sub_file.parts or sub_file.name == "install_manifest.json":
                continue
            files[rel] = compute_sha256(sub_file)
    return files


def install_aac(root_dir: Path, target_version: str, source_override: Path | None = None) -> bool:
    print(f"\n=> Installing Antigravity Agent Core ({target_version}) to: {root_dir}")
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = root_dir / ".agents-backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Preserve existing custom brain context and MCP configurations
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

    preserved_mcp: str | None = None
    existing_mcp = root_dir / ".agents" / "mcp_config.json"
    if existing_mcp.is_file():
        try:
            preserved_mcp = existing_mcp.read_text(encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Notice reading mcp_config.json: {e}\n")

    # 2. Acquire release source in a temporary directory or from local source
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        source_dir = tmp_dir / "source"
        cloned = False

        if source_override and Path(source_override).is_dir():
            source_dir = Path(source_override)
            cloned = True
        else:
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
                    with tarfile.open(tar_path, "r:gz") as tar:  # nosemgrep: trailofbits.python.tarfile-extractall-traversal.tarfile-extractall-traversal
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

        # Air-gapped / Local checkout fallback
        if not cloned or not source_dir.exists():
            local_repo = Path(__file__).resolve().parent
            if (local_repo / "AGENTS.md").is_file() and (local_repo / ".agents").is_dir():
                print(f"=> Using local repository as installation source: {local_repo}")
                source_dir = local_repo
                cloned = True

        if not cloned or not source_dir.exists():
            print("=> ERROR: Unable to acquire release sources from GitHub or local repository.")
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
        if (source_dir / "agent.md").is_file():
            copy_managed_item(source_dir / "agent.md", root_dir / "agent.md", backup_dir)
        copy_managed_item(source_dir / ".agents", root_dir / ".agents", backup_dir)
        copy_managed_item(source_dir / "scripts", root_dir / "scripts", backup_dir)
        
        if (source_dir / ".githooks").is_dir():
            copy_managed_item(source_dir / ".githooks", root_dir / ".githooks", backup_dir)

        env_example_src = source_dir / ".env.example"
        env_example_dst = root_dir / ".env.example"
        if env_example_src.is_file() and not env_example_dst.exists():
            shutil.copy2(env_example_src, env_example_dst)

        # Bootstrap contracts for verification gates (only if missing in target)
        if (source_dir / "intent.yaml").is_file() and not (root_dir / "intent.yaml").exists():
            copy_managed_item(source_dir / "intent.yaml", root_dir / "intent.yaml", backup_dir)
        if (source_dir / "handoff.json").is_file() and not (root_dir / "handoff.json").exists():
            copy_managed_item(source_dir / "handoff.json", root_dir / "handoff.json", backup_dir)

        # 5. Restore preserved brain and MCP configuration files
        for bf, content in preserved_brain.items():
            bf_path = root_dir / ".agents" / "brain" / bf
            bf_path.parent.mkdir(parents=True, exist_ok=True)
            bf_path.write_text(content, encoding="utf-8")

        if preserved_mcp:
            mcp_path = root_dir / ".agents" / "mcp_config.json"
            try:
                old_data = json.loads(preserved_mcp)
                new_data = json.loads(mcp_path.read_text(encoding="utf-8")) if mcp_path.is_file() else {}
                old_servers = old_data.get("mcpServers", {})
                new_servers = new_data.get("mcpServers", {})
                new_data["mcpServers"] = {**new_servers, **old_servers}
                mcp_path.write_text(json.dumps(new_data, indent=2), encoding="utf-8")
            except Exception as exc:
                sys.stderr.write(f"Notice merging mcp_config: {exc}\n")

        # 6. Ensure .gitignore has scratch and backup rules
        gitignore_path = root_dir / ".gitignore"
        try:
            if gitignore_path.is_file():
                gi_text = gitignore_path.read_text(encoding="utf-8")
                updates = []
                if ".agents/scratch/" not in gi_text:
                    updates.append(".agents/scratch/")
                if ".agents-backups/" not in gi_text:
                    updates.append(".agents-backups/")
                if updates:
                    block = "\n\n# Antigravity Managed Directories\n" + "\n".join(updates) + "\n"
                    gitignore_path.write_text(gi_text.rstrip() + block, encoding="utf-8")
            else:
                gitignore_path.write_text("# Antigravity Managed Directories\n.agents/scratch/\n.agents-backups/\n", encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Gitignore update notice: {e}\n")

        # 7. Configure Git Hooks safely if .git exists
        if (root_dir / ".git").is_dir() and (root_dir / ".githooks" / "pre-commit").is_file():
            try:
                if os.name != "nt":
                    (root_dir / ".githooks" / "pre-commit").chmod(0o755)
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

        # 8. Clean up accidental workflow files in target project safely
        wf_dir = root_dir / ".github" / "workflows"
        if wf_dir.is_dir():
            for f in ("agent-gates.yml", "agentic-cicd.yml"):
                wf_file = wf_dir / f
                if wf_file.is_file():
                    wf_file.unlink()
            try:
                if not any(wf_dir.iterdir()):
                    wf_dir.rmdir()
                gh_dir = root_dir / ".github"
                if not any(gh_dir.iterdir()):
                    gh_dir.rmdir()
            except OSError as err:
                sys.stderr.write(f"Notice: .github cleanup: {err}\n")

        # 9. Record Installation Manifest for Source Integrity & Audits
        manifest_files: dict[str, str] = {}
        managed_roots = [
            root_dir / "AGENTS.md",
            root_dir / "GEMINI.md",
            root_dir / "agent.md",
            root_dir / ".env.example",
            root_dir / "scripts",
            root_dir / ".agents",
            root_dir / ".githooks",
        ]
        for mroot in managed_roots:
            if mroot.is_file():
                rel = str(mroot.relative_to(root_dir)).replace("\\", "/")
                manifest_files[rel] = compute_sha256(mroot)
            elif mroot.is_dir():
                manifest_files.update(scan_managed_dir(mroot, root_dir))

        manifest_data = {
            "installed_version": target_version.lstrip("v"),
            "source_repository": REMOTE_REPO,
            "source_revision": target_version,
            "install_timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "installed_by": "AAC Universal Installer",
            "managed_files": manifest_files,
            "backup_dir": str(backup_dir.relative_to(root_dir)).replace("\\", "/"),
        }
        manifest_path = root_dir / ".agents" / "install_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        return True


def run_upgrade(root_dir: Path, target_version: str) -> bool:
    """Delegates to native cross-platform installation."""
    return install_aac(root_dir, target_version)


def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Universal Installer & Upgrade Engine")
    parser.add_argument("path", nargs="?", default=".", help="Project workspace root")
    parser.add_argument("--version", default=None, help="Target specific AAC version/tag to install")
    parser.add_argument("--revision", default=None, help="Target specific Git revision/branch/tag")
    parser.add_argument("--check", action="store_true", help="Check for latest version without installing")
    parser.add_argument("--force", "--reinstall", action="store_true", dest="force", help="Force re-installation")
    parser.add_argument("--status", "--audit", action="store_true", help="Audit installed files and source integrity")
    parser.add_argument("--repair", action="store_true", help="Repair corrupted or missing managed files")
    parser.add_argument("--rollback", nargs="?", const="", default=None, help="Roll back to previous backup snapshot")
    parser.add_argument("--uninstall", action="store_true", help="Safely uninstall AAC from target workspace")
    parser.add_argument("--source-dir", default=None, help="Local source directory to install from (offline / air-gapped)")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()

    if args.status:
        audit = audit_installation(root_dir)
        print("=" * 60)
        print("🔍 AAC Source Integrity & Installation Audit")
        print("=" * 60)
        print(f"Installed Version:    v{audit['installed_version']}")
        print(f"Source Repository:    {audit['source_repository']}")
        print(f"Source Revision:      {audit['source_revision']}")
        print(f"Install Timestamp:    {audit['install_timestamp']}")
        print(f"Integrity Status:     {audit['integrity_status']}")
        print(f"Total Managed Files:  {audit['total_managed_files']}")
        print(f"Intact Files:         {len(audit['intact_files'])}")
        print(f"Modified Files:       {len(audit['modified_files'])}")
        print(f"Missing Files:        {len(audit['missing_files'])}")
        if audit["modified_files"]:
            print("\n⚠️ Locally Modified Files:")
            for f in audit["modified_files"][:10]:
                print(f"  • {f}")
        if audit["missing_files"]:
            print("\n❌ Missing Files:")
            for f in audit["missing_files"][:10]:
                print(f"  • {f}")
        sys.exit(0 if audit["integrity_status"] in ("INTACT", "UNVERIFIED") else 1)

    if args.rollback is not None:
        target_snapshot = args.rollback.strip() if args.rollback else None
        success = run_rollback(root_dir, target_backup=target_snapshot)
        sys.exit(0 if success else 1)

    if args.uninstall:
        success = run_uninstall(root_dir)
        sys.exit(0 if success else 1)

    source_override = Path(args.source_dir).resolve() if args.source_dir else None

    if args.repair:
        success = run_repair(root_dir, source_override=source_override)
        sys.exit(0 if success else 1)

    status = check_update_status(root_dir)
    target_ver = args.version or args.revision or str(status["latest_version"])
    if not target_ver.startswith("v") and re.match(r"^\d+\.\d+\.\d+", target_ver):
        target_ver = f"v{target_ver}"

    print("=" * 60)
    print("🚀 Antigravity Agent Core (AAC) Universal Installer")
    print("=" * 60)
    print(f"Current Workspace Version: v{status['current_version']}")
    print(f"Target Installation:       {target_ver}")

    if not status["has_update"] and not args.force and not args.version and not args.revision and status["current_version"] != "0.0.0" and not args.source_dir:
        print("\n✨ You are already running the latest world-class AAC agent!")
        return

    if status["has_update"] or status["current_version"] == "0.0.0" or args.source_dir or args.version or args.revision:
        action = "Update" if status["current_version"] != "0.0.0" else "Install"
        print(f"\n🎉 Performing {action}: {target_ver}")

    if args.check:
        print("\nRun 'python3 install.py' to apply this configuration effortlessly.")
        return

    success = install_aac(root_dir, target_ver, source_override=source_override)
    if success:
        print("\n" + "=" * 60)
        print(f"✅ AAC successfully configured to {target_ver}!")
        print("💡 All custom memories (.agents/brain/memory.md) and rules were preserved.")
        print("=" * 60)
        verify_script = root_dir / "scripts" / "verify.py"
        if verify_script.is_file():
            print("\n=> Running post-install verification gates...")
            sub_env = os.environ.copy()
            sub_env["PYTHONIOENCODING"] = "utf-8"
            sub_env["PYTHONUTF8"] = "1"
            subprocess.run([sys.executable, str(verify_script), "--execute", "--terse"], cwd=root_dir, env=sub_env)
        health_script = root_dir / "scripts" / "health_check.py"
        if health_script.is_file():
            print("\n=> Running post-install health check...")
            subprocess.run([sys.executable, str(health_script)], cwd=root_dir)
    else:
        print("\n❌ Installation failed. Check logs above or rollback with 'python3 install.py --rollback'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

