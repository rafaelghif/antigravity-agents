import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestAgentEval(unittest.TestCase):
    def test_anti_dummy_compliance(self):
        forbidden_tokens = ['// TODO', 'mock_', 'dummy_', 'passw' + 'ord123']
        src_files = list((ROOT / '.agents').rglob('*.md'))
        for f in src_files:
            if 'skill.md' in f.name.lower() or 'task_template' in f.name.lower():
                continue
            text = f.read_text(errors='ignore').lower()
            found = [t for t in forbidden_tokens if t in text]
            self.assertFalse(found, f'Agent evaluation failed: Found forbidden tokens {found} in {f}')

    def test_security_skill_presence(self):
        impl_content = (ROOT / '.agents/agents/staff-backend.md').read_text()
        self.assertIn('security', impl_content, 'Backend is missing mandatory security context.')

if __name__ == '__main__':
    unittest.main()
