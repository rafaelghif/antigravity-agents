#!/usr/bin/env python3
"""
AAC Autonomous Memory Consolidator (Hierarchical Cross-Session Memory Engine):
Synchronizes, updates, and persists working context (active_context.md) and
long-term project memory (memory.md) across conversation turns and session boundaries.
Inspired by MemGPT/Letta tiered memory and Cline Memory Bank architecture.
"""

from __future__ import annotations

import json, sys, re, argparse
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVE_PATH = ROOT / ".agents/brain/active_context.md"
DEFAULT_MEMORY_PATH = ROOT / ".agents/brain/memory.md"

HEADER_MAP: dict[str, str] = {
    "current goal": "focus",
    "task focus": "focus",
    "key decisions": "decisions",
    "invariants": "decisions",
    "recent accomplishments": "accomplishments",
    "milestones": "accomplishments",
    "next immediate steps": "next_steps",
    "next steps": "next_steps",
    "blockers": "blockers",
    "known issues": "blockers"
}


def _match_header_key(header_title: str) -> str | None:
    """Matches a section header to a predefined context key."""
    for pattern, key in HEADER_MAP.items():
        if pattern in header_title:
            return key
    return None


def load_active_context(path: Path = DEFAULT_ACTIVE_PATH) -> dict[str, list[str]]:
    """Loads sections from active_context.md into a structured dictionary."""
    if not path.exists():
        return {
            "focus": ["No active focus specified."],
            "decisions": [],
            "accomplishments": [],
            "next_steps": [],
            "blockers": ["None. All gates green."]
        }

    content = path.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {
        "focus": [],
        "decisions": [],
        "accomplishments": [],
        "next_steps": [],
        "blockers": []
    }
    
    current_key = "focus"

    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("## "):
            matched_key = _match_header_key(trimmed[3:].strip().lower())
            if matched_key:
                current_key = matched_key
        elif trimmed.startswith("- ") or trimmed.startswith("* "):
            item = trimmed[2:].strip()
            if item:
                sections[current_key].append(item)

    return sections


def format_active_context(sections: dict[str, list[str]]) -> str:
    """Formats structured context sections into clean, high-density markdown."""
    focus_lines = "\n".join(f"- {item}" for item in sections.get("focus", ["Active engineering in progress."]))
    dec_lines = "\n".join(f"- {item}" for item in sections.get("decisions", ["Follow strict L9 verification and Caveman token efficiency."]))
    acc_lines = "\n".join(f"- {item}" for item in sections.get("accomplishments", ["Maintained 100% green verification status."]))
    next_lines = "\n".join(f"- {item}" for item in sections.get("next_steps", ["Execute next scheduled user roadmap items."]))
    blk_lines = "\n".join(f"- {item}" for item in sections.get("blockers", ["None. All systems operational."]))

    return f"""# ⚡ Active Session Context & Working Memory

> [!IMPORTANT]
> This file is dynamically maintained across conversation turns and session boundaries.
> It holds active task focus, recent milestones, and immediate next steps.

## 🎯 Current Goal & Task Focus
{focus_lines}

## 📌 Key Decisions & Invariants
{dec_lines}

## 🚀 Recent Accomplishments
{acc_lines}

## ⏳ Next Immediate Steps
{next_lines}

## ⚠️ Blockers & Known Issues
{blk_lines}
"""


import contextlib
import os
import tempfile
import time


@contextlib.contextmanager
def file_lock(target_path: Path, timeout: float = 10.0, poll_interval: float = 0.05):
    """Cross-platform advisory file lock to serialize concurrent read-modify-write cycles."""
    lock_path = target_path.with_name(f".{target_path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    fd = None

    if sys.platform != "win32":
        try:
            import fcntl
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except (BlockingIOError, OSError):
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Timed out waiting for file lock: {lock_path}")
                    time.sleep(poll_interval)
            yield
        finally:
            if fd is not None:
                try:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except Exception as exc:
                    _ = exc
                try:
                    os.close(fd)
                except Exception as exc:
                    _ = exc
    else:
        acquired = False
        lock_fd = None
        while time.time() - start_time < timeout:
            try:
                lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                acquired = True
                break
            except FileExistsError:
                time.sleep(poll_interval)
        if not acquired:
            try:
                if lock_path.exists() and (time.time() - lock_path.stat().st_mtime > 30):
                    lock_path.unlink(missing_ok=True)
            except Exception as exc:
                _ = exc
            raise TimeoutError(f"Timed out waiting for Windows file lock: {lock_path}")
        try:
            yield
        finally:
            if lock_fd is not None:
                try:
                    os.close(lock_fd)
                except Exception as exc:
                    _ = exc
            try:
                lock_path.unlink(missing_ok=True)
            except Exception as exc:
                _ = exc


def save_active_context(sections: dict[str, list[str]], path: Path = DEFAULT_ACTIVE_PATH) -> bool:
    """Atomically writes active context markdown to disk using unique tempfile."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = format_active_context(sections)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix="active_ctx_",
            suffix=".tmp",
            delete=False
        ) as temp_f:
            temp_f.write(content)
            temp_path = Path(temp_f.name)
        temp_path.replace(path)
        return True
    except Exception as exc:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError as err:
                _ = err
        sys.stderr.write(f"Save active context notice: {exc}\n")
        raise


def update_active_state(
    focus: str | None = None,
    accomplishment: str | None = None,
    next_step: str | None = None,
    blocker: str | None = None,
    path: Path = DEFAULT_ACTIVE_PATH
) -> bool:
    """Updates active working context with new items under process file lock."""
    with file_lock(path):
        sections = load_active_context(path)

        if focus:
            sections["focus"] = [focus]
        if accomplishment and accomplishment not in sections["accomplishments"]:
            sections["accomplishments"].insert(0, accomplishment)
            sections["accomplishments"] = sections["accomplishments"][:10]
        if next_step and next_step not in sections["next_steps"]:
            sections["next_steps"].insert(0, next_step)
            sections["next_steps"] = sections["next_steps"][:10]
        if blocker:
            sections["blockers"] = [blocker]

        return save_active_context(sections, path)


def parse_latest_user_intent(lines: list[str]) -> str | None:
    """Extracts the latest meaningful user input from transcript lines, stripping XML metadata."""
    for line in reversed(lines):
        try:
            data = json.loads(line)
            if "USER_INPUT" in str(data.get("type", "")):
                content = str(data.get("content", "")).strip()
                if len(content) > 5 and not content.startswith("/"):
                    clean = re.sub(r'<USER_REQUEST>\s*', '', content)
                    clean = re.sub(r'\s*</USER_REQUEST>.*', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<[^>]+>', '', clean).strip()
                    if clean and len(clean) > 5:
                        return clean
        except Exception:
            continue
    return None


def sync_transcript_to_memory(
    transcript_path: Path,
    active_path: Path = DEFAULT_ACTIVE_PATH,
    memory_path: Path = DEFAULT_MEMORY_PATH
) -> bool:
    """Reads recent transcript turns and synchronizes working memory."""
    if not transcript_path.exists():
        return False

    try:
        lines = transcript_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        latest_intent = parse_latest_user_intent(lines)
        if latest_intent:
            clean_intent = latest_intent.replace("\n", " ").strip()
            if len(clean_intent) > 140:
                trimmed = clean_intent[:140].rsplit(" ", 1)[0]
                clean_intent = (trimmed if trimmed else clean_intent[:140]) + "..."
            update_active_state(focus=clean_intent, path=active_path)
            return True
    except Exception as e:
        sys.stderr.write(f"Memory consolidator transcript notice: {e}\n")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Autonomous Memory Consolidator")
    parser.add_argument("--update-focus", metavar="TEXT", help="Update current task focus")
    parser.add_argument("--add-accomplishment", metavar="TEXT", help="Add completed milestone")
    parser.add_argument("--add-next", metavar="TEXT", help="Add next immediate step")
    parser.add_argument("--set-blocker", metavar="TEXT", help="Set active blocker or clear with None")
    parser.add_argument("--sync-transcript", metavar="PATH", help="Sync active state from transcript.jsonl")
    parser.add_argument("--show", action="store_true", help="Print current active working memory")
    args = parser.parse_args()

    if args.show:
        ctx = load_active_context()
        print(format_active_context(ctx))
        return

    if args.update_focus or args.add_accomplishment or args.add_next or args.set_blocker:
        update_active_state(
            focus=args.update_focus,
            accomplishment=args.add_accomplishment,
            next_step=args.add_next,
            blocker=args.set_blocker
        )
        print("=> SUCCESS: Active working memory updated.")
        return

    if args.sync_transcript:
        synced = sync_transcript_to_memory(Path(args.sync_transcript))
        if synced:
            print("=> SUCCESS: Working memory synchronized from transcript.")
        else:
            print("=> NOTICE: No new active context to sync.")
        return

    print("Usage: python3 scripts/memory_consolidator.py --update-focus '<task>' OR --sync-transcript <path> OR --show")


if __name__ == "__main__":
    main()
