import unittest
import tempfile
import shutil
import os
import subprocess

class TestUpgradeFlow(unittest.TestCase):

    def setUp(self):
        # Create a temporary target directory
        self.test_dir = tempfile.mkdtemp()
        
        # Determine paths
        self.src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        self.install_sh = os.path.join(self.src_dir, "install.sh")
        
    def tearDown(self):
        # Cleanup temporary target directory
        shutil.rmtree(self.test_dir)

    def test_installer_upgrade_backup(self):
        # 1. Create a dummy old installation in target
        old_agents_dir = os.path.join(self.test_dir, ".agents")
        os.makedirs(old_agents_dir, exist_ok=True)
        
        old_board = os.path.join(old_agents_dir, "tasks/board.md")
        os.makedirs(os.path.dirname(old_board), exist_ok=True)
        with open(old_board, 'w') as f:
            f.write("old task board content")
            
        old_agents_md = os.path.join(self.test_dir, "AGENTS.md")
        with open(old_agents_md, 'w') as f:
            f.write("old agents rules content")
            
        # 2. Run install.sh pointing to self.test_dir
        # Bypass unit tests execution inside validate.py of target run to speed up
        env = os.environ.copy()
        env["BYPASS_TESTS"] = "true"
        
        res = subprocess.run(
            ['bash', self.install_sh, self.test_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        self.assertEqual(res.returncode, 0, f"Installer failed: {res.stderr}\n{res.stdout}")
        
        # 3. Assert backup folders exist
        contents = os.listdir(self.test_dir)
        backup_dirs = [c for c in contents if c.startswith(".agents_backup_")]
        backup_files = [c for c in contents if c.startswith("AGENTS.md.backup_")]
        
        self.assertEqual(len(backup_dirs), 1, f"Backup directory was not created: {contents}")
        self.assertEqual(len(backup_files), 1, f"Backup AGENTS.md was not created: {contents}")
        
        # Verify backed up content
        backup_board = os.path.join(self.test_dir, backup_dirs[0], "tasks/board.md")
        self.assertTrue(os.path.exists(backup_board))
        with open(backup_board, 'r') as f:
            self.assertEqual(f.read(), "old task board content")
            
        backup_agents_md = os.path.join(self.test_dir, backup_files[0])
        self.assertTrue(os.path.exists(backup_agents_md))
        with open(backup_agents_md, 'r') as f:
            self.assertEqual(f.read(), "old agents rules content")

if __name__ == '__main__':
    unittest.main()
