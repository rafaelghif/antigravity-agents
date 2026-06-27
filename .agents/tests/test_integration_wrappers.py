import unittest
import subprocess
import os
import shutil

class TestIntegrationWrappers(unittest.TestCase):

    def test_helper_sh_no_args_prints_help(self):
        res = subprocess.run(
            ['./helper.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Antigravity Agent Core (AAC) V2 CLI Command Helper", res.stdout)

    def test_helper_sh_unknown_command_fails(self):
        res = subprocess.run(
            ['./helper.sh', 'invalidcommandxyz'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: Unknown command 'invalidcommandxyz'", res.stdout)

    def test_helper_sh_relative_subdirectory_execution(self):
        temp_subdir = "src/presentation"
        os.makedirs(temp_subdir, exist_ok=True)
        res = subprocess.run(
            ['../../helper.sh'],
            cwd=temp_subdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Antigravity Agent Core (AAC) V2 CLI Command Helper", res.stdout)

    @unittest.skipIf(not shutil.which("pwsh"), "PowerShell Core (pwsh) not installed")
    def test_helper_ps1_no_args_prints_help(self):
        res = subprocess.run(
            ['pwsh', './helper.ps1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Antigravity Agent Core (AAC) V2 CLI Command Helper", res.stdout)

if __name__ == '__main__':
    unittest.main()
