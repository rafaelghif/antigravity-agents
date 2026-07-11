import unittest
import os
import re

class TestPlatformDrift(unittest.TestCase):
    """Platform drift guard tests checking structural parity between Bash and PowerShell scripts."""

    def test_bootstrap_version_parity(self):
        """Verify version matches between AGENTS.md and bootstrap.py."""
        # 1. Parse version from AGENTS.md
        agents_version = None
        self.assertTrue(os.path.exists("AGENTS.md"), "AGENTS.md must exist in root.")
        with open("AGENTS.md", "r", encoding="utf-8") as f:
            m = re.search(r"-\s+\*\*Version:\*\*\s*([0-9.]+)", f.read())
            if m:
                agents_version = m.group(1)
        self.assertIsNotNone(agents_version, "Could not extract version from AGENTS.md")

        # 2. Check bootstrap.py version matches
        bootstrap_py = ".agents/scripts/cli/commands/bootstrap.py"
        self.assertTrue(os.path.exists(bootstrap_py), "bootstrap.py must exist.")
        with open(bootstrap_py, "r", encoding="utf-8") as f:
            py_content = f.read()
        self.assertIn(f'AAC_VERSION = "{agents_version}"', py_content, "bootstrap.py version does not match AGENTS.md")

    def test_directory_creation_delegation(self):
        """Verify the wrappers delegate setup and execution to helper.py bootstrap."""
        with open("bootstrap.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py bootstrap", sh_content, "bootstrap.sh does not delegate to helper.py bootstrap")

        with open("bootstrap.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py bootstrap", ps_content, "bootstrap.ps1 does not delegate to helper.py bootstrap")

    def test_helper_cli_target_parity(self):
        """Verify that helper.sh and helper.ps1 wrapper scripts call the same target helper script."""
        with open("helper.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py", sh_content, "helper.sh does not target cli/helper.py")

        with open("helper.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py", ps_content, "helper.ps1 does not target cli/helper.py")

    def test_installer_delegation_parity(self):
        """Verify that install.sh and install.ps1 both delegate to helper.py install."""
        with open("install.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        self.assertTrue("helper.py" in sh_content and "install" in sh_content, "install.sh does not delegate to helper.py install")

        with open("install.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        self.assertTrue("helper.py" in ps_content and "install" in ps_content, "install.ps1 does not delegate to helper.py install")

if __name__ == "__main__":
    unittest.main()
