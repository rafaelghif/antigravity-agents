import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "hooks"))

from scripts.hooks import pre_invoke_master, hook_utils

class TestHooks(unittest.TestCase):
    def test_detect_skills_from_text(self):
        self.assertIn("design", pre_invoke_master.detect_skills_from_text("fix button styling and tailwind css"))
        self.assertIn("architecture", pre_invoke_master.detect_skills_from_text("add postgres database schema and orm"))
        self.assertIn("security", pre_invoke_master.detect_skills_from_text("implement jwt auth and sanitize input"))
        self.assertIn("verification", pre_invoke_master.detect_skills_from_text("write pytest unit test for endpoint"))
        self.assertIn("devops", pre_invoke_master.detect_skills_from_text("create dockerfile and kubernetes manifest"))
        self.assertIn("code-quality", pre_invoke_master.detect_skills_from_text("arbitrary text"))

    def test_parse_skills_from_frontmatter_inline(self):
        fm = "skills: [architecture, verification, security]"
        skills = pre_invoke_master.parse_skills_from_frontmatter(fm)
        self.assertEqual(skills, ["architecture", "verification", "security"])

    def test_parse_skills_from_frontmatter_multiline(self):
        fm = "skills:\n  - architecture\n  - code-quality"
        skills = pre_invoke_master.parse_skills_from_frontmatter(fm)
        self.assertIn("architecture", skills)
        self.assertIn("code-quality", skills)

    def test_get_context_includes_grounding_baseline(self):
        ctx = pre_invoke_master.get_context(None)
        self.assertIn("=== CODEBASE GROUNDING BASELINE ===", ctx)
        self.assertIn("Ecosystem:", ctx)
        self.assertIn("OS/Arch:", ctx)

    def test_get_context_with_frameworks_and_test_runners(self):
        from unittest.mock import patch
        mock_grounding = {
            "ecosystems": {"node": ["package.json"]},
            "environment": {"platform": "linux", "architecture": "x86_64", "machine": "x86_64"},
            "package_managers": {"lockfile_managed": ["pnpm"], "available_cli": ["git", "pnpm"]},
            "frameworks": [{"name": "React", "ecosystem": "node", "package": "react"}, {"name": "Next.js", "ecosystem": "node", "package": "next"}],
            "testing": ["vitest", "playwright"],
            "dependencies": {"node": ["react", "next"]},
        }
        with patch("scripts.grounding.ground_workspace", return_value=mock_grounding):
            ctx = pre_invoke_master.get_context(None)
            self.assertIn("Frameworks: React, Next.js", ctx)
            self.assertIn("Test Runners: vitest, playwright", ctx)
            self.assertIn("OS/Arch: linux (x86_64)", ctx)
            self.assertIn("Tooling: Lockfile: pnpm | CLI: git, pnpm", ctx)

    def test_pre_tool_quality_gate_denies_git_tampering(self):
        from unittest.mock import patch
        import io
        import json
        from scripts.hooks import pre_tool_quality_gate
        payload = json.dumps({
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/repo/.git/config", "CodeContent": "bad"}
            }
        }).encode("utf-8")
        with patch("sys.stdin.buffer.read", return_value=payload), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            pre_tool_quality_gate.main()
            out = json.loads(mock_stdout.getvalue().strip())
            self.assertEqual(out.get("decision"), "deny")
            self.assertIn("Direct modification of .git", out.get("reason", ""))

    def test_pre_tool_quality_gate_denies_private_key(self):
        from unittest.mock import patch
        import io
        import json
        from scripts.hooks import pre_tool_quality_gate
        dummy_secret = "-----" + "BEGIN RSA " + "PRIVATE KEY-----" + "\nMIIE..."
        payload = json.dumps({
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/repo/src/secret.key", "CodeContent": dummy_secret}
            }
        }).encode("utf-8")
        with patch("sys.stdin.buffer.read", return_value=payload), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            pre_tool_quality_gate.main()
            out = json.loads(mock_stdout.getvalue().strip())
            self.assertEqual(out.get("decision"), "deny")
            self.assertIn("Potential secret", out.get("reason", ""))

    def test_pre_tool_quality_gate_allows_safe_files(self):
        from unittest.mock import patch
        import io
        import json
        from scripts.hooks import pre_tool_quality_gate
        payload = json.dumps({
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/repo/src/main.py", "CodeContent": "print('hello world')"}
            }
        }).encode("utf-8")
        with patch("sys.stdin.buffer.read", return_value=payload), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            pre_tool_quality_gate.main()
            out = json.loads(mock_stdout.getvalue().strip())
            self.assertEqual(out.get("decision"), "allow")

    def test_pre_tool_quality_gate_denies_git_without_trailing_slash(self):
        from unittest.mock import patch
        import io
        import json
        from scripts.hooks import pre_tool_quality_gate
        for target in (".git", "/repo/.git", "./.git", "submodule/.git"):
            payload = json.dumps({
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": target, "CodeContent": "bad"}
                }
            }).encode("utf-8")
            with patch("sys.stdin.buffer.read", return_value=payload), \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                pre_tool_quality_gate.main()
                out = json.loads(mock_stdout.getvalue().strip())
                self.assertEqual(out.get("decision"), "deny", f"Failed to deny target: {target}")

    def test_pre_tool_quality_gate_denies_pkcs8_and_api_keys(self):
        from unittest.mock import patch
        import io
        import json
        from scripts.hooks import pre_tool_quality_gate
        test_secrets = [
            "-----" + "BEGIN PRIVATE " + "KEY-----\nMIIE...",
            "-----" + "BEGIN ENCRYPTED PRIVATE " + "KEY-----\nMIIE...",
            "AI" + "za" + "SyD-Xxxx1234567890abcdefghijklmn",
            "github_" + "pat_" + "11AAAAAAA01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
            "sk-" + "proj-" + "1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdef",
            "sk-" + "ant-" + "1234567890abcdefghijklmnopqrstuvwxyz12",
        ]
        for sec in test_secrets:
            payload = json.dumps({
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "/repo/src/config.py", "CodeContent": sec}
                }
            }).encode("utf-8")
            with patch("sys.stdin.buffer.read", return_value=payload), \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                pre_tool_quality_gate.main()
                out = json.loads(mock_stdout.getvalue().strip())
                self.assertEqual(out.get("decision"), "deny", f"Failed to deny secret: {sec}")

    def test_pre_invoke_master_omits_unpopulated_dag_anchor(self):
        ctx = pre_invoke_master.get_context(None)
        self.assertNotIn("=== DAG ANCHOR ===", ctx)

    def test_pre_invoke_master_main_uses_ephemeral_message(self):
        from unittest.mock import patch
        import io
        import json
        with patch("sys.stdin.read", return_value='{"transcriptPath": null}'), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            pre_invoke_master.main()
            raw = mock_stdout.getvalue().strip()
            out = json.loads(raw)
            self.assertIn("injectSteps", out)
            self.assertIn("ephemeralMessage", out["injectSteps"][0])
            self.assertNotIn("silence", out["injectSteps"][0])

if __name__ == "__main__":
    unittest.main()
