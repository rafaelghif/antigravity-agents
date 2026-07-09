import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import issue

class CaptureStringIO(io.StringIO):
    def __init__(self, initial_value='', path=None, writes_list=None):
        super().__init__(initial_value)
        self.path = path
        self.writes_list = writes_list
        
    def write(self, s):
        if self.writes_list is not None:
            self.writes_list.append((self.path, s))
        return super().write(s)

class TestIssueCommand(unittest.TestCase):

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_checkout_issue_records_assignee(self, mock_file, mock_exists, mock_sub):
        mock_exists.side_effect = lambda path: True
        
        mock_profiles_json = json.dumps({
            "profiles": [
                {"name": "dev-alice", "email": "alice@corp.com", "active": True}
            ]
        })
        mock_issue_md = "---\nid: issue-225\ntitle: Test\nstatus: open\n---\n"
        
        writes = []
        
        def open_side_effect(path, mode='r', encoding=None):
            if 'w' in mode:
                return CaptureStringIO(path=path, writes_list=writes)
            else:
                if "git_profiles.json" in path:
                    return io.StringIO(mock_profiles_json)
                else:
                    return io.StringIO(mock_issue_md)
                    
        mock_file.side_effect = open_side_effect
        mock_sub.return_value = MagicMock(returncode=0)
        
        issue.run(["checkout", "issue-225"])
        
        self.assertTrue(len(writes) > 0)
        written_content = writes[0][1]
        self.assertIn("assignee: dev-alice", written_content)

if __name__ == '__main__':
    unittest.main()
