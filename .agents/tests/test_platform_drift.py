import unittest
import os
import re

class TestPlatformDrift(unittest.TestCase):
    """Platform drift guard tests checking structural parity between Bash and PowerShell scripts."""

    def test_bootstrap_version_parity(self):
        """Verify version strings are identical in bootstrap scripts and match AGENTS.md."""
        # 1. Parse version from AGENTS.md
        agents_version = None
        self.assertTrue(os.path.exists("AGENTS.md"), "AGENTS.md must exist in root.")
        with open("AGENTS.md", "r", encoding="utf-8") as f:
            m = re.search(r"-\s+\*\*Version:\*\*\s*([0-9.]+)", f.read())
            if m:
                agents_version = m.group(1)
        self.assertIsNotNone(agents_version, "Could not extract version from AGENTS.md")

        # 2. Check bootstrap.sh
        self.assertTrue(os.path.exists("bootstrap.sh"), "bootstrap.sh must exist.")
        with open("bootstrap.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        sh_versions = re.findall(r"Version:\s*([0-9.]+)", sh_content)
        # Also check version string embedded in the python re.sub script inside bootstrap.sh
        sh_subs = re.findall(r'"- \*\*Version:\*\* ([0-9.]+)"', sh_content) + re.findall(r'Version:\*\* ([0-9.]+)', sh_content)
        
        # 3. Check bootstrap.ps1
        self.assertTrue(os.path.exists("bootstrap.ps1"), "bootstrap.ps1 must exist.")
        with open("bootstrap.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        ps_versions = re.findall(r"Version:\s*([0-9.]+)", ps_content)

        # Assert all versions are synced with AGENTS.md
        self.assertIn(agents_version, sh_content, "bootstrap.sh does not contain the current version.")
        self.assertIn(agents_version, ps_content, "bootstrap.ps1 does not contain the current version.")

    def test_directory_creation_parity(self):
        """Verify the directories created in bootstrap.sh and bootstrap.ps1 are identical."""
        # Extract mkdir directories from bootstrap.sh
        with open("bootstrap.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        sh_dirs = set(re.findall(r"mkdir -p (\.agents/\S+)", sh_content))

        # Extract directories from bootstrap.ps1
        with open("bootstrap.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        
        # Find the array of directories under $Dirs = @( ... )
        m = re.search(r"\$Dirs\s*=\s*@\(\s*([^)]+)\)", ps_content, re.DOTALL)
        self.assertIsNotNone(m, r"Could not locate \$Dirs array in bootstrap.ps1")
        ps_dirs = set()
        for line in m.group(1).splitlines():
            # Strip whitespace, quotes, and commas cleanly
            line_strip = line.strip().replace('"', '').replace("'", "").replace(",", "").strip()
            if line_strip:
                ps_dirs.add(line_strip)

        self.assertEqual(sh_dirs, ps_dirs, f"Directory creation skew detected! Bash creates {sh_dirs} but PowerShell creates {ps_dirs}.")

    def test_helper_cli_target_parity(self):
        """Verify that helper.sh and helper.ps1 wrapper scripts call the same target helper script."""
        with open("helper.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py", sh_content, "helper.sh does not target cli/helper.py")

        with open("helper.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        self.assertIn(".agents/scripts/cli/helper.py", ps_content, "helper.ps1 does not target cli/helper.py")

    def test_installer_copy_parity(self):
        """Verify that install.sh and install.ps1 both copy the same core files during install/upgrade."""
        with open("install.sh", "r", encoding="utf-8") as f:
            sh_content = f.read()
        
        # Extract files copied in install.sh (e.g. cp "$EXTRACTED_DIR/file" ...)
        sh_copies = set(re.findall(r'cp\s+["\']\$EXTRACTED_DIR/([^"\']+)["\']', sh_content))
        expected = {"helper.sh", "helper.ps1", "bootstrap.sh", "bootstrap.ps1", "Dockerfile", "AGENTS.md"}
        for item in expected:
            self.assertIn(item, sh_copies, f"install.sh is missing copying of '{item}'")

        with open("install.ps1", "r", encoding="utf-8") as f:
            ps_content = f.read()
        
        # Extract files copied in install.ps1 (e.g. Join-Path $ExtractedDir "file")
        ps_copies = set(re.findall(r'Join-Path\s+\$ExtractedDir\s+["\']([^"\']+)["\']', ps_content))
        for item in expected:
            self.assertIn(item, ps_copies, f"install.ps1 is missing copying of '{item}'")

if __name__ == "__main__":
    unittest.main()
