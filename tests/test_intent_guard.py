import sys
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import intent_guard

class TestIntentGuard(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_auto_initialize_default_intent(self):
        success = intent_guard.check_intent(self.root)
        self.assertTrue(success)
        intent_file = self.root / "intent.yaml"
        self.assertTrue(intent_file.is_file())
        self.assertIn("status: \"DONE\"", intent_file.read_text(encoding="utf-8"))

    def test_valid_done_with_completed_tasks(self):
        intent_file = self.root / "intent.yaml"
        intent_file.write_text('name: "Test"\nstatus: "DONE"\ndescription: "Test intent"\n', encoding="utf-8")
        tasks_dir = self.root / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "01_test.yaml").write_text('id: "01_test"\nstatus: "DONE"\n', encoding="utf-8")

        success = intent_guard.check_intent(self.root)
        self.assertTrue(success)

    def test_done_with_unfinished_tasks_fails(self):
        intent_file = self.root / "intent.yaml"
        intent_file.write_text('name: "Test"\nstatus: "DONE"\ndescription: "Test intent"\n', encoding="utf-8")
        tasks_dir = self.root / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "01_test.yaml").write_text('id: "01_test"\nstatus: "IN_PROGRESS"\n', encoding="utf-8")

        success = intent_guard.check_intent(self.root)
        self.assertFalse(success)

    def test_in_progress_with_pending_tasks(self):
        intent_file = self.root / "intent.yaml"
        intent_file.write_text('name: "Test"\nstatus: "IN_PROGRESS"\ndescription: "Test intent"\n', encoding="utf-8")
        tasks_dir = self.root / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "01_test.yaml").write_text('id: "01_test"\nstatus: "IN_PROGRESS"\n', encoding="utf-8")

        success = intent_guard.check_intent(self.root)
        self.assertTrue(success)

    def test_in_progress_with_empty_tasks_fails(self):
        intent_file = self.root / "intent.yaml"
        intent_file.write_text('name: "Test"\nstatus: "IN_PROGRESS"\ndescription: "Test intent"\n', encoding="utf-8")
        tasks_dir = self.root / "tasks"
        tasks_dir.mkdir()

        success = intent_guard.check_intent(self.root)
        self.assertFalse(success)

    def test_invalid_yaml_schema_fails(self):
        intent_file = self.root / "intent.yaml"
        intent_file.write_text('status: "DONE"\ndescription: "No name"\n', encoding="utf-8")

        success = intent_guard.check_intent(self.root)
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
