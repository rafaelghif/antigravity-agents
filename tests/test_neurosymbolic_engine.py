import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.neurosymbolic_engine import validate_handoff

class TestNeurosymbolicEngine(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            'task_id': 'TASK-001',
            'worker_role': 'staff-backend',
            'summary': 'Implemented robust endpoint.',
            'modifications': [
                {'filepath': 'app/main.py', 'change_type': 'UPDATE', 'description': 'Added route.'}
            ],
            'tests': [
                {'test_command': 'python3 -m unittest', 'status': 'PASSED', 'output_snippet': 'OK'}
            ],
            'confidence_score': 0.95,
            'requires_human': False
        }

    def test_valid_handoff_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_path = Path(tmpdir) / "handoff.json"
            tf_path.write_text(json.dumps(self.valid_payload), encoding="utf-8")
            self.assertTrue(validate_handoff(tf_path))

    def test_missing_required_key_fails(self):
        payload = dict(self.valid_payload)
        del payload['worker_role']
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_path = Path(tmpdir) / "handoff.json"
            tf_path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_handoff(tf_path))

    def test_missing_file_fails(self):
        self.assertFalse(validate_handoff(Path('/non/existent/path/handoff.json')))

    def test_invalid_json_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_path = Path(tmpdir) / "handoff.json"
            tf_path.write_text('{invalid_json: true', encoding="utf-8")
            self.assertFalse(validate_handoff(tf_path))

    def test_invalid_confidence_range_fails(self):
        payload = dict(self.valid_payload)
        payload['confidence_score'] = 1.5
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_path = Path(tmpdir) / "handoff.json"
            tf_path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_handoff(tf_path))

        payload['confidence_score'] = -0.1
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_path = Path(tmpdir) / "handoff.json"
            tf_path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_handoff(tf_path))

if __name__ == '__main__':
    unittest.main()
