import os
import unittest
import shutil
import subprocess
import re

class TestInstallParity(unittest.TestCase):
    def test_installation_and_parity(self):
        core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        temp_target = "/tmp/compare_install_target_test"

        if os.path.exists(temp_target):
            shutil.rmtree(temp_target, ignore_errors=True)
        os.makedirs(temp_target, exist_ok=True)

        try:
            # 1. Run installer using the local source repository helper.py directly
            import sys
            env = os.environ.copy()
            for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"]:
                env.pop(key, None)
            res = subprocess.run(
                [sys.executable, os.path.join(core_dir, ".agents/scripts/cli/helper.py"), "install", temp_target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            self.assertEqual(res.returncode, 0, f"Installation failed: {res.stderr}")

            # 2. Check exclusions
            leaked_files = [
                "bootstrap.sh",
                "bootstrap.ps1",
                "install.sh",
                "install.ps1",
                "requirements.txt",
                "pyproject.toml",
                ".github"
            ]
            for item in leaked_files:
                path = os.path.join(temp_target, item)
                self.assertFalse(os.path.exists(path), f"Leaked file in target project: {item}")

            # 3. Check placeholder resolution
            check_files = {
                "AGENTS.md": ["{{NAME}}", "{{PRODUCT}}", "{{STACK}}", "{{VERSION}}", "{{LAYOUT}}"],
                ".agents/rules.md": ["{{NAME}}", "{{STACK}}", "{{TEST_CMD}}"],
                ".agents/schema.md": ["{{NAME}}", "{{STACK}}", "{{ARCH}}"],
                ".agents/mcp_config.json": ["disabled", "alwaysAllow"]
            }
            for filename, markers in check_files.items():
                path = os.path.join(temp_target, filename)
                self.assertTrue(os.path.exists(path), f"Missing target file: {filename}")
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if filename != ".agents/mcp_config.json":
                    for marker in markers:
                        self.assertNotIn(marker, content, f"Placeholder {marker} not resolved in {filename}")
                else:
                    for marker in markers:
                        self.assertIn(marker, content, f"MCP config missing synchronized field {marker}")

            # 4. Check core rule isolation
            core_rules = [
                "When modifying CLI commands, options, or core settings, the agent MUST explicitly review and synchronize the installer files",
                "Template & Wrapper Parity"
            ]
            for filename in ["AGENTS.md", ".agents/rules.md"]:
                path = os.path.join(temp_target, filename)
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for rule in core_rules:
                        self.assertNotIn(rule, content, f"Core rule leaked into target {filename}: {rule}")

        finally:
            if os.path.exists(temp_target):
                shutil.rmtree(temp_target, ignore_errors=True)
