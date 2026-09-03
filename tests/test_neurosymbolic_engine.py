import json
import tempfile
import unittest
from pathlib import Path

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
        with tempfile.NamedTemporaryFile('w', suffix='.json') as tf:
            json.dump(self.valid_payload, tf)
            tf.flush()
            self.assertTrue(validate_handoff(Path(tf.name)))

    def test_missing_required_key_fails(self):
        payload = dict(self.valid_payload)
        del payload['worker_role']
        with tempfile.NamedTemporaryFile('w', suffix='.json') as tf:
            json.dump(payload, tf)
            tf.flush()
            self.assertFalse(validate_handoff(Path(tf.name)))

    def test_missing_file_fails(self):
        self.assertFalse(validate_handoff(Path('/non/existent/path/handoff.json')))

    def test_invalid_json_fails(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json') as tf:
            tf.write('{invalid_json: true')
            tf.flush()
            self.assertFalse(validate_handoff(Path(tf.name)))

if __name__ == '__main__':
    unittest.main()
