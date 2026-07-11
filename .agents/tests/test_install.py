import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import patch, MagicMock

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import install

class TestInstallCommand(unittest.TestCase):

    def setUp(self):
        self.old_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        self.run_patcher = patch('subprocess.run')
        self.mock_run = self.run_patcher.start()
        self.mock_run.return_value = MagicMock(returncode=0)

    def tearDown(self):
        self.run_patcher.stop()
        os.chdir(self.old_cwd)
        shutil.rmtree(self.temp_dir)

    def test_should_exclude(self):
        # Excluded items
        self.assertTrue(install.should_exclude(".agents/tasks/board.md"))
        self.assertTrue(install.should_exclude(".agents/issues/issue_12.md"))
        self.assertTrue(install.should_exclude(".agents/git_profiles.json"))
        self.assertTrue(install.should_exclude("__pycache__/file.pyc"))
        self.assertTrue(install.should_exclude(".git/config"))
        
        # Included items
        self.assertFalse(install.should_exclude(".agents/scripts/validate.py"))
        self.assertFalse(install.should_exclude(".agents/memory/templates/rules.md.template"))
        self.assertFalse(install.should_exclude("helper.sh"))
        self.assertFalse(install.should_exclude("Dockerfile"))

    @patch('os.path.exists', return_value=True)
    def test_run_install_backup(self, mock_exists):
        # Verify backups and paths creation during run
        with patch('shutil.move') as mock_move, \
             patch('shutil.copy') as mock_copy, \
             patch('shutil.copy2') as mock_copy2, \
             patch('os.walk') as mock_walk, \
             patch('importlib.util.spec_from_file_location') as mock_spec:
             
            mock_walk.return_value = [
                ('/src', [], ['helper.sh', 'AGENTS.md', 'dummy.pyc'])
            ]
            
            # Mock spec loading for bootstrap
            mock_spec.return_value = MagicMock(loader=MagicMock())
            
            try:
                dest_path = os.path.join(self.temp_dir, "dest")
                install.run([dest_path])
            except SystemExit:
                pass
                
            # Verify backup triggers
            mock_move.assert_called()
            mock_copy.assert_called()

if __name__ == '__main__':
    unittest.main()
