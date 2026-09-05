import sys
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

try:
    from scripts.neurosymbolic_engine import validate_handoff
except ImportError:
    validate_handoff = None


class TestConfigAlignment(unittest.TestCase):
    def test_mcp_config_alignment(self):
        example_path = ROOT / ".agents" / "mcp_config.json.example"
        actual_path = ROOT / ".agents" / "mcp_config.json"
        self.assertTrue(example_path.is_file(), ".agents/mcp_config.json.example must exist")

        with open(example_path, "r", encoding="utf-8") as f:
            ex_data = json.load(f)

        self.assertIn("mcpServers", ex_data, "mcpServers key must exist in example config")
        ex_servers = ex_data.get("mcpServers", {})
        self.assertIsInstance(ex_servers, dict)
        self.assertTrue(len(ex_servers) > 0, "mcpServers must not be empty")

        for srv_name, srv in ex_servers.items():
            self.assertIn("command", srv, f"Server {srv_name} missing command")
            self.assertIsInstance(srv["command"], str)
            self.assertIn("args", srv, f"Server {srv_name} missing args")
            self.assertIsInstance(srv["args"], list)
            if "env" in srv:
                self.assertIsInstance(srv["env"], dict)

        if actual_path.is_file():
            with open(actual_path, "r", encoding="utf-8") as f:
                act_data = json.load(f)
            act_servers = act_data.get("mcpServers", {})

            # Bidirectional server keys parity
            self.assertEqual(
                set(ex_servers.keys()),
                set(act_servers.keys()),
                f"Server keys mismatch: {set(ex_servers.keys()) ^ set(act_servers.keys())}"
            )

            # Deep property parity per server
            for name in ex_servers:
                ex_srv = ex_servers[name]
                act_srv = act_servers[name]
                self.assertEqual(
                    set(ex_srv.keys()),
                    set(act_srv.keys()),
                    f"Property mismatch for server {name}: {set(ex_srv.keys()) ^ set(act_srv.keys())}"
                )
                for prop in ("command", "args"):
                    self.assertEqual(type(ex_srv[prop]), type(act_srv[prop]), f"Type mismatch for {name}.{prop}")
                    if prop == "args":
                        self.assertTrue(all(isinstance(a, str) for a in act_srv[prop]))
                if "env" in ex_srv:
                    self.assertEqual(
                        set(ex_srv["env"].keys()),
                        set(act_srv["env"].keys()),
                        f"Env keys mismatch for server {name}"
                    )

    def test_antigravity_settings_alignment(self):
        example_path = ROOT / ".agents" / "antigravity-settings.example.json"
        self.assertTrue(example_path.is_file(), ".agents/antigravity-settings.example.json must exist")

        with open(example_path, "r", encoding="utf-8") as f:
            ex_settings = json.load(f)

        # Baseline requirements for example
        self.assertEqual(ex_settings.get("toolPermission"), "always-proceed")
        self.assertEqual(ex_settings.get("enableTerminalSandbox"), False)
        self.assertEqual(ex_settings.get("allowNonWorkspaceAccess"), True)
        self.assertEqual(ex_settings.get("artifactReviewPolicy"), "auto")

        ex_perms = ex_settings.get("permissions", {})
        self.assertIsInstance(ex_perms, dict)
        self.assertIn("allow", ex_perms)
        self.assertIn("deny", ex_perms)
        self.assertIn("ask", ex_perms)
        self.assertTrue(len(ex_perms["allow"]) > 0)
        self.assertTrue(len(ex_perms["deny"]) > 0)

        # Compare with workspace settings if present
        workspace_settings_path = ROOT / ".agents" / "antigravity-settings.json"
        if workspace_settings_path.is_file():
            with open(workspace_settings_path, "r", encoding="utf-8") as f:
                act_settings = json.load(f)

            # 100% bidirectional key parity
            self.assertEqual(
                set(ex_settings.keys()),
                set(act_settings.keys()),
                f"Workspace settings keys mismatch: {set(ex_settings.keys()) ^ set(act_settings.keys())}"
            )

            # Permissions parity
            act_perms = act_settings.get("permissions", {})
            self.assertEqual(set(ex_perms.keys()), set(act_perms.keys()))
            self.assertEqual(set(ex_perms["allow"]), set(act_perms["allow"]))
            self.assertEqual(ex_perms["deny"], act_perms["deny"])
            self.assertEqual(ex_perms["ask"], act_perms["ask"])

            # Baseline values
            self.assertEqual(act_settings.get("toolPermission"), "always-proceed")
            self.assertEqual(act_settings.get("enableTerminalSandbox"), False)
            self.assertEqual(act_settings.get("allowNonWorkspaceAccess"), True)
            self.assertEqual(act_settings.get("artifactReviewPolicy"), "auto")

        # Compare with global CLI settings if present
        cli_settings_path = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
        if cli_settings_path.is_file():
            with open(cli_settings_path, "r", encoding="utf-8") as f:
                cli_settings = json.load(f)

            self.assertEqual(
                set(ex_settings.keys()),
                set(cli_settings.keys()),
                f"CLI settings keys mismatch: {set(ex_settings.keys()) ^ set(cli_settings.keys())}"
            )
            self.assertEqual(cli_settings.get("toolPermission"), "always-proceed")
            self.assertEqual(cli_settings.get("enableTerminalSandbox"), False)
            self.assertEqual(cli_settings.get("allowNonWorkspaceAccess"), True)
            self.assertEqual(cli_settings.get("artifactReviewPolicy"), "auto")

    def test_env_files_alignment(self):
        example_path = ROOT / ".env.example"
        actual_path = ROOT / ".env"
        self.assertTrue(example_path.is_file(), ".env.example must exist")

        def get_keys(p):
            keys = []
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        keys.append(line.split("=", 1)[0])
            return keys

        ex_keys = get_keys(example_path)
        self.assertTrue(len(ex_keys) > 0, ".env.example must define environment variables")

        if actual_path.is_file():
            act_keys = get_keys(actual_path)
            self.assertEqual(
                set(ex_keys),
                set(act_keys),
                f"Mismatch in .env keys: {set(ex_keys) ^ set(act_keys)}"
            )

        # Assert parity with env-required.json
        env_req_path = ROOT / ".agents" / "brain" / "env-required.json"
        if env_req_path.is_file():
            with open(env_req_path, "r", encoding="utf-8") as f:
                req_data = json.load(f)
            for req_key in req_data:
                self.assertIn(
                    req_key,
                    set(ex_keys),
                    f"Required env key {req_key} from env-required.json missing in .env.example"
                )

    def test_handoff_template_alignment(self):
        tpl_path = ROOT / "handoff_template.json"
        act_path = ROOT / "handoff.json"
        self.assertTrue(tpl_path.is_file(), "handoff_template.json must exist")

        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl_data = json.load(f)

        required_keys = {"task_id", "worker_role", "summary", "modifications", "tests", "confidence_score", "requires_human"}
        self.assertEqual(
            set(tpl_data.keys()),
            required_keys,
            f"handoff_template keys mismatch with required neurosymbolic schema: {set(tpl_data.keys()) ^ required_keys}"
        )

        if act_path.is_file():
            with open(act_path, "r", encoding="utf-8") as f:
                act_data = json.load(f)
            self.assertEqual(
                set(tpl_data.keys()),
                set(act_data.keys()),
                f"handoff_template and handoff.json keys mismatch: {set(tpl_data.keys()) ^ set(act_data.keys())}"
            )
            # Compare modification element schema
            if tpl_data["modifications"] and act_data["modifications"]:
                self.assertEqual(
                    set(tpl_data["modifications"][0].keys()),
                    set(act_data["modifications"][0].keys()),
                    "Modification item schema mismatch"
                )
            # Compare test element schema
            if tpl_data["tests"] and act_data["tests"]:
                self.assertEqual(
                    set(tpl_data["tests"][0].keys()),
                    set(act_data["tests"][0].keys()),
                    "Test item schema mismatch"
                )

        if validate_handoff is not None:
            self.assertTrue(validate_handoff(tpl_path), "handoff_template.json must pass neurosymbolic validation")


if __name__ == '__main__':
    unittest.main()
