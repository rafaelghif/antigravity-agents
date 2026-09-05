import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.memory_consolidator import (
    load_active_context,
    format_active_context,
    update_active_state,
    sync_transcript_to_memory,
    save_active_context
)

class TestMemoryConsolidator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.active_path = Path(self.tmp_dir.name) / "active_context.md"
        self.memory_path = Path(self.tmp_dir.name) / "memory.md"
        
        initial_content = """# ⚡ Active Session Context & Working Memory

## 🎯 Current Goal & Task Focus
- Implement feature X.

## 🚀 Recent Accomplishments
- Step 1 completed.

## ⏳ Next Immediate Steps
- Step 2 execute.

## ⚠️ Blockers & Known Issues
- None.
"""
        self.active_path.write_text(initial_content, encoding="utf-8")
        self.memory_path.write_text("# Memory\n", encoding="utf-8")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_load_and_format_active_context(self):
        sections = load_active_context(self.active_path)
        self.assertIn("Implement feature X.", sections["focus"])
        self.assertIn("Step 1 completed.", sections["accomplishments"])
        self.assertIn("Step 2 execute.", sections["next_steps"])

        formatted = format_active_context(sections)
        self.assertIn("Implement feature X.", formatted)
        self.assertIn("## 🎯 Current Goal & Task Focus", formatted)

    def test_update_active_state(self):
        updated = update_active_state(
            focus="Build resilient payment engine",
            accomplishment="Added idempotency key check",
            next_step="Deploy database migration",
            blocker="Waiting for staging credentials",
            path=self.active_path
        )
        self.assertTrue(updated)

        sections = load_active_context(self.active_path)
        self.assertEqual(sections["focus"], ["Build resilient payment engine"])
        self.assertIn("Added idempotency key check", sections["accomplishments"])
        self.assertIn("Deploy database migration", sections["next_steps"])
        self.assertEqual(sections["blockers"], ["Waiting for staging credentials"])

    def test_sync_transcript_to_memory(self):
        transcript_file = Path(self.tmp_dir.name) / "transcript.jsonl"
        turns = [
            {"type": "USER_INPUT", "content": "Tolong buatkan endpoint auth JWT"},
            {"type": "PLANNER_RESPONSE", "content": "Executing auth..."}
        ]
        with transcript_file.open("w", encoding="utf-8") as f:
            for t in turns:
                f.write(json.dumps(t) + "\n")

        synced = sync_transcript_to_memory(transcript_file, active_path=self.active_path, memory_path=self.memory_path)
        self.assertTrue(synced)

        sections = load_active_context(self.active_path)
        self.assertTrue(any("auth JWT" in item for item in sections["focus"]))

    def test_sync_transcript_to_memory_malformed(self):
        transcript_file = Path(self.tmp_dir.name) / "transcript_bad.jsonl"
        with transcript_file.open("w", encoding="utf-8") as f:
            f.write("not a valid json\n")
            f.write("{}\n")
            f.write(json.dumps({"type": "USER_INPUT", "content": ""}) + "\n")
        
        synced = sync_transcript_to_memory(transcript_file, active_path=self.active_path, memory_path=self.memory_path)
        self.assertFalse(synced)

    def test_concurrent_active_state_updates(self):
        import concurrent.futures
        
        def do_update(idx: int):
            return update_active_state(
                accomplishment=f"Concurrent milestone {idx}",
                path=self.active_path
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(do_update, i) for i in range(10)]
            results = [f.result() for f in futures]

        self.assertTrue(all(results))
        sections = load_active_context(self.active_path)
        self.assertGreater(len(sections["accomplishments"]), 0)
        self.assertTrue(any("Concurrent milestone" in acc for acc in sections["accomplishments"]))

    def test_windows_stale_lock_recovery(self):
        import time
        from unittest.mock import patch
        from scripts.memory_consolidator import file_lock

        target = Path(self.tmp_dir.name) / "test_win_lock.md"
        lock_path = Path(self.tmp_dir.name) / ".test_win_lock.md.lock"
        lock_path.write_text("abandoned", encoding="utf-8")
        stale_time = time.time() - 60
        os.utime(lock_path, (stale_time, stale_time))

        with patch("sys.platform", "win32"):
            # Should recover from stale lock immediately during polling without raising TimeoutError
            acquired = False
            with file_lock(target, timeout=2.0, poll_interval=0.05):
                acquired = True
            self.assertTrue(acquired)


if __name__ == '__main__':
    unittest.main()
