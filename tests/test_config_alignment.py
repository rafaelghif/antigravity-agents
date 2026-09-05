import sys
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

class TestConfigAlignment(unittest.TestCase):
    def test_mcp_config_alignment(self):
        example_path = ROOT / ".agents" / "mcp_config.json.example"
        actual_path = ROOT / ".agents" / "mcp_config.json"
        self.assertTrue(example_path.is_file(), ".agents/mcp_config.json.example must exist")
        self.assertTrue(actual_path.is_file(), ".agents/mcp_config.json must exist")

        with open(example_path, "r", encoding="utf-8") as f:
            ex_data = json.load(f)
        with open(actual_path, "r", encoding="utf-8") as f:
            act_data = json.load(f)

        ex_servers = ex_data.get("mcpServers", {})
        act_servers = act_data.get("mcpServers", {})

        # Assert identical server keys
        self.assertEqual(
            set(ex_servers.keys()),
            set(act_servers.keys()),
            f"Server keys mismatch: {set(ex_servers.keys()) ^ set(act_servers.keys())}"
        )

        # Assert schema parity for each server
        for name in ex_servers:
            ex_srv = ex_servers[name]
            act_srv = act_servers[name]
            self.assertEqual(
                set(ex_srv.keys()),
                set(act_srv.keys()),
                f"Property mismatch for server {name}: {set(ex_srv.keys()) ^ set(act_srv.keys())}"
            )
            for prop in ("command", "args"):
                if prop in ex_srv:
                    self.assertEqual(type(ex_srv[prop]), type(act_srv[prop]))
            if "env" in ex_srv:
                self.assertEqual(set(ex_srv["env"].keys()), set(act_srv["env"].keys()))

    def test_antigravity_settings_alignment(self):
        example_path = ROOT / ".agents" / "antigravity-settings.example.json"
        self.assertTrue(example_path.is_file(), ".agents/antigravity-settings.example.json must exist")

        with open(example_path, "r", encoding="utf-8") as f:
            ex_settings = json.load(f)

        # Compare with workspace settings and global CLI settings if present
        candidates = [ROOT / ".agents" / "antigravity-settings.json", Path.home() / ".gemini" / "antigravity-cli" / "settings.json"]
        found_any = False
        for actual_path in candidates:
            if actual_path.is_file():
                found_any = True
                with open(actual_path, "r", encoding="utf-8") as f:
                    act_settings = json.load(f)

                # Assert all example keys exist in actual settings
                for k in ex_settings:
                    self.assertIn(k, act_settings, f"Key {k} from example missing in {actual_path}")

                # Assert identical permissions structure
                ex_perms = ex_settings.get("permissions", {})
                act_perms = act_settings.get("permissions", {})
                self.assertIn("allow", act_perms)
                self.assertIn("deny", act_perms)
                self.assertIn("ask", act_perms)

                # Assert required boolean and string baselines
                self.assertEqual(act_settings.get("toolPermission"), "always-proceed")
                self.assertEqual(act_settings.get("enableTerminalSandbox"), False)
                self.assertEqual(act_settings.get("allowNonWorkspaceAccess"), True)
                self.assertEqual(act_settings.get("artifactReviewPolicy"), "auto")

        self.assertTrue(found_any, "At least one actual settings file should be available for verification")

    def test_env_files_alignment(self):
        example_path = ROOT / ".env.example"
        actual_path = ROOT / ".env"
        self.assertTrue(example_path.is_file(), ".env.example must exist")
        if actual_path.is_file():
            def get_keys(p):
                keys = []
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            keys.append(line.split("=", 1)[0])
                return keys

            ex_keys = get_keys(example_path)
            act_keys = get_keys(actual_path)
            self.assertEqual(
                set(ex_keys),
                set(act_keys),
                f"Mismatch in .env keys: {set(ex_keys) ^ set(act_keys)}"
            )

if __name__ == '__main__':
    unittest.main()
