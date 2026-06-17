import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.validate as validate
import utils

class TestValidateCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as workspace
        self.test_dir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Setup basic .agents folder
        self.agents_dir = os.path.join(self.test_dir, ".agents")
        os.makedirs(self.agents_dir)
        os.makedirs(os.path.join(self.agents_dir, "locks"))
        os.makedirs(os.path.join(self.agents_dir, "schemas"))
        os.makedirs(os.path.join(self.agents_dir, "adrs"))
        
        # Write basic memory file
        with open(os.path.join(self.agents_dir, "memory.md"), 'w') as f:
            f.write("# Memory\n- **State Flag**: COMPLETED\n")
            
        # Write basic schema index and schemas
        with open(os.path.join(self.agents_dir, "schema.md"), 'w') as f:
            f.write("# Schema Index\n- [Default Module](file://./schemas/default.md)\n")
        with open(os.path.join(self.agents_dir, "schemas", "default.md"), 'w') as f:
            f.write("# Default Domain Schema\n")
            
        # Write basic adr index and adr file
        with open(os.path.join(self.agents_dir, "adr.md"), 'w') as f:
            f.write("# ADR Index\n- [ADR-001: test](file://./adrs/001-test.md)\n")
        with open(os.path.join(self.agents_dir, "adrs", "001-test.md"), 'w') as f:
            f.write("# ADR-001\n## Context\nTest\n## Decision\nTest\n## Consequences\nTest\n")
            
        # Write mock git config files
        with open(".gitignore", 'w') as f:
            f.write(".agents/locks/\n")
            
    def tearDown(self):
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.test_dir)
        
    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_successful_validation(self, mock_run, mock_check_output):
        def side_effect(args, **kwargs):
            if "remote" in args:
                return b"origin\n"
            elif "rev-parse" in args:
                return b"main\n"
            elif "merge-base" in args:
                return b"main\n"
            return b""
        mock_check_output.side_effect = side_effect
        
        # Patch sys.exit to catch validation status
        with patch('sys.exit') as mock_exit:
            validate.run([])
            mock_exit.assert_called_once_with(0)
            
    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_failed_validation_on_missing_adr(self, mock_run, mock_check_output):
        def side_effect(args, **kwargs):
            if "remote" in args:
                return b"origin\n"
            elif "rev-parse" in args:
                return b"main\n"
            elif "merge-base" in args:
                return b"main\n"
            return b""
        mock_check_output.side_effect = side_effect
        
        # Remove adr index to cause validation failure
        os.remove(os.path.join(self.agents_dir, "adr.md"))
        
        with patch('sys.exit') as mock_exit:
            validate.run([])
            mock_exit.assert_called_once_with(1)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_base_branch_modification_failed(self, mock_run, mock_check_output):
        def side_effect(args, **kwargs):
            if "remote" in args:
                return b"origin\n"
            elif "rev-parse" in args:
                if "--abbrev-ref" in args:
                    return b"main\n"
                return b"main\n"
            elif "status" in args:
                return b" M src/core.py\n"
            return b""
        mock_check_output.side_effect = side_effect
        
        with patch('sys.exit') as mock_exit:
            validate.run([])
            mock_exit.assert_called_once_with(1)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_module_locking_failed(self, mock_run, mock_check_output):
        def side_effect(args, **kwargs):
            if "remote" in args:
                return b"origin\n"
            elif "rev-parse" in args:
                if "--abbrev-ref" in args:
                    return b"issue-10-test\n"
                return b"main\n"
            elif "status" in args:
                return b" M src/core.py\n"
            return b""
        mock_check_output.side_effect = side_effect
        
        with patch('sys.exit') as mock_exit:
            validate.run([])
            mock_exit.assert_called_once_with(1)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_issue_alignment_failed(self, mock_run, mock_check_output):
        def side_effect(args, **kwargs):
            if "remote" in args:
                return b"origin\n"
            elif "rev-parse" in args:
                if "--abbrev-ref" in args:
                    return b"issue-99-mismatch\n"
                return b"main\n"
            elif "status" in args:
                return b""
            return b""
        mock_check_output.side_effect = side_effect
        
        # Write issue file #99
        os.makedirs(os.path.join(self.agents_dir, "issues"), exist_ok=True)
        with open(os.path.join(self.agents_dir, "issues", "issue_099.md"), 'w') as f:
            f.write("---\nid: 99\ntitle: \"Mismatch Test\"\nstatus: open\nassignee: Agent\ncreated_at: 2026-06-17\nclosed_at: null\n---\n")
            
        with patch('sys.exit') as mock_exit:
            validate.run([])
            mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
