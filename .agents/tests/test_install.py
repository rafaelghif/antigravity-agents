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
        self.assertTrue(install.should_exclude("AGENTS.md"))
        self.assertTrue(install.should_exclude("__pycache__/file.pyc"))
        self.assertTrue(install.should_exclude(".git/config"))
        self.assertTrue(install.should_exclude("Dockerfile"))
        self.assertTrue(install.should_exclude(".gitignore"))
        self.assertTrue(install.should_exclude(".antigravityignore"))
        self.assertTrue(install.should_exclude("README.md"))
        
        # Included items
        self.assertFalse(install.should_exclude(".agents/scripts/validate.py"))
        self.assertFalse(install.should_exclude(".agents/memory/templates/rules.md.template"))
        self.assertFalse(install.should_exclude(".agents/blueprints/clean-architecture.md"))
        self.assertFalse(install.should_exclude(".agents/workflows/sync-memory.md"))
        self.assertFalse(install.should_exclude("helper.sh"))

    @patch('os.path.exists', return_value=True)
    def test_run_install_backup(self, mock_exists):
        # Verify backups and paths creation during run
        with patch('shutil.move') as mock_move, \
             patch('shutil.copy') as mock_copy, \
             patch('shutil.copy2') as mock_copy2, \
             patch('os.walk') as mock_walk, \
             patch('importlib.util.spec_from_file_location') as mock_spec:
             
            source_root = os.path.abspath(os.path.join(os.path.dirname(install.__file__), "../../../.."))
            def mock_walk_side_effect(top, *args, **kwargs):
                if "dest" in top and "backup" in top:
                    return [
                        (top, [], ['helper.sh', 'AGENTS.md', 'dummy.pyc'])
                    ]
                else:
                    return [
                        (source_root, [], ['helper.sh', 'AGENTS.md', 'dummy.pyc'])
                    ]
            mock_walk.side_effect = mock_walk_side_effect
            
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

    @patch('shutil.move')
    @patch('shutil.copy2')
    @patch('os.walk')
    @patch('os.path.exists')
    @patch('importlib.util.spec_from_file_location')
    def test_run_install_restores_backup(self, mock_spec, mock_exists, mock_walk, mock_copy2, mock_move):
        # Setup paths: mock_exists returns True for everything to trigger backup and restore paths
        mock_exists.side_effect = lambda path: True
        
        source_root = os.path.abspath(os.path.join(os.path.dirname(install.__file__), "../../../.."))
        # Mock os.walk: First walk is for source files, second walk is for backup files
        def mock_walk_side_effect(top, *args, **kwargs):
            if "dest" in top and "backup" in top:
                # backup_agents walk
                return [
                    (top, [], ['git_profiles.json', 'rules.md'])
                ]
            else:
                # source_root walk
                return [
                    (source_root, [], ['helper.sh', 'AGENTS.md'])
                ]
        mock_walk.side_effect = mock_walk_side_effect
        mock_spec.return_value = MagicMock(loader=MagicMock())
        
        try:
            dest_path = os.path.join(self.temp_dir, "dest")
            install.run([dest_path])
        except SystemExit:
            pass
            
        # Verify restore copy2 calls (should restore rules.md and git_profiles.json)
        restore_called = False
        for args, kwargs in mock_copy2.call_args_list:
            if args:
                src = args[0]
                if "git_profiles.json" in src or "rules.md" in src:
                    restore_called = True
        self.assertTrue(restore_called)

    @patch('shutil.copy2')
    @patch('os.walk')
    @patch('os.path.exists', return_value=False)
    @patch('importlib.util.spec_from_file_location')
    def test_run_install_copies_missing_critical_files(self, mock_spec, mock_exists, mock_walk, mock_copy2):
        source_root = os.path.abspath(os.path.join(os.path.dirname(install.__file__), "../../../.."))
        mock_walk.return_value = [
            (source_root, [], ['AGENTS.md', 'rules.md', 'milestones.md', 'security-policy.md', 'some_other_file.py'])
        ]
        mock_spec.return_value = MagicMock(loader=MagicMock())
        
        try:
            dest_path = os.path.join(self.temp_dir, "dest")
            install.run([dest_path])
        except SystemExit:
            pass
            
        copied_files = []
        for args, kwargs in mock_copy2.call_args_list:
            if args:
                copied_files.append(os.path.basename(args[0]))
                
        # AGENTS.md is critical and missing, it should be copied (rules.md is excluded and generated via bootstrap)
        self.assertIn('AGENTS.md', copied_files)
        self.assertNotIn('rules.md', copied_files)
        self.assertNotIn('milestones.md', copied_files)
        self.assertNotIn('security-policy.md', copied_files)
        # some_other_file.py is not excluded, it should be copied
        self.assertIn('some_other_file.py', copied_files)

if __name__ == '__main__':
    unittest.main()
