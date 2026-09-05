import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from install import (
    audit_installation,
    compute_sha256,
    install_aac,
    run_repair,
    run_rollback,
    run_uninstall,
)


class TestInstallLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp_dir.name)
        # Create minimal valid source repository
        self.src_dir = tempfile.TemporaryDirectory()
        self.src = Path(self.src_dir.name)
        (self.src / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
        (self.src / "GEMINI.md").write_text("# Bootstrap\nAGENTS.md\n", encoding="utf-8")
        (self.src / "agent.md").write_text("# Agent\n", encoding="utf-8")
        (self.src / ".agents" / "brain").mkdir(parents=True)
        (self.src / ".agents" / "config.json").write_text('{"core_version": "4.47.0"}', encoding="utf-8")
        (self.src / "scripts").mkdir(parents=True)
        (self.src / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")

    def tearDown(self):
        self.tmp_dir.cleanup()
        self.src_dir.cleanup()

    def test_install_generates_manifest(self):
        success = install_aac(self.target, "v4.47.0", source_override=self.src)
        self.assertTrue(success)

        manifest_file = self.target / ".agents" / "install_manifest.json"
        self.assertTrue(manifest_file.is_file())
        mdata = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(mdata["installed_version"], "4.47.0")
        self.assertEqual(mdata["source_revision"], "v4.47.0")
        self.assertIn("managed_files", mdata)
        self.assertGreater(len(mdata["managed_files"]), 0)

        # Audit should pass with INTACT
        audit = audit_installation(self.target)
        self.assertEqual(audit["integrity_status"], "INTACT")
        self.assertEqual(len(audit["modified_files"]), 0)
        self.assertEqual(len(audit["missing_files"]), 0)

    def test_audit_detects_tampered_files(self):
        install_aac(self.target, "v4.47.0", source_override=self.src)

        # Tamper with an installed managed file
        (self.target / "AGENTS.md").write_text("# Tampered Agents content\n", encoding="utf-8")

        audit = audit_installation(self.target)
        self.assertEqual(audit["integrity_status"], "COMPROMISED")
        self.assertIn("AGENTS.md", audit["modified_files"])

    def test_audit_detects_missing_files(self):
        install_aac(self.target, "v4.47.0", source_override=self.src)

        # Delete a managed file
        (self.target / "AGENTS.md").unlink()

        audit = audit_installation(self.target)
        self.assertEqual(audit["integrity_status"], "COMPROMISED")
        self.assertIn("AGENTS.md", audit["missing_files"])

    def test_repair_restores_tampered_files(self):
        install_aac(self.target, "v4.47.0", source_override=self.src)
        (self.target / "AGENTS.md").write_text("# Tampered\n", encoding="utf-8")

        # Run repair
        success = run_repair(self.target, source_override=self.src)
        self.assertTrue(success)

        # Integrity restored
        audit = audit_installation(self.target)
        self.assertEqual(audit["integrity_status"], "INTACT")
        self.assertIn("# Agents", (self.target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_rollback_restores_previous_state(self):
        # 1. First installation
        install_aac(self.target, "v4.44.0", source_override=self.src)
        (self.target / "AGENTS.md").write_text("# Version 1 Content\n", encoding="utf-8")

        # 2. Second installation (creates backup)
        (self.src / "AGENTS.md").write_text("# Version 2 Content\n", encoding="utf-8")
        install_aac(self.target, "v4.47.0", source_override=self.src)
        self.assertIn("# Version 2", (self.target / "AGENTS.md").read_text(encoding="utf-8"))

        # 3. Rollback
        success = run_rollback(self.target)
        self.assertTrue(success)
        self.assertIn("# Version 1", (self.target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_rollback_prunes_orphaned_files(self):
        # 1. First installation (v1)
        install_aac(self.target, "v4.44.0", source_override=self.src)
        (self.target / "scripts" / "tool.py").write_text("print('v1')\n", encoding="utf-8")

        # 2. Second installation introduces a new tool
        (self.src / "scripts" / "new_tool.py").write_text("print('new')\n", encoding="utf-8")
        install_aac(self.target, "v4.47.0", source_override=self.src)
        self.assertTrue((self.target / "scripts" / "new_tool.py").is_file())

        # 3. Rollback must prune new_tool.py
        success = run_rollback(self.target)
        self.assertTrue(success)
        self.assertFalse((self.target / "scripts" / "new_tool.py").exists())
        self.assertTrue((self.target / "scripts" / "tool.py").is_file())

    def test_install_generates_project_tailored_intent(self):
        install_aac(self.target, "v4.47.0", source_override=self.src)
        intent_path = self.target / "intent.yaml"
        self.assertTrue(intent_path.is_file())
        content = intent_path.read_text(encoding="utf-8")
        self.assertIn(self.target.name, content)
        self.assertNotIn("Antigravity Fully Agentic Looping System", content)

    def test_uninstall_safely_removes_managed_files(self):
        install_aac(self.target, "v4.47.0", source_override=self.src)
        (self.target / ".agents" / "brain" / "memory.md").write_text("# User Memories\n", encoding="utf-8")
        (self.target / "user_code.py").write_text("print('user project')\n", encoding="utf-8")

        success = run_uninstall(self.target)
        self.assertTrue(success)

        # User project code must be untouched
        self.assertTrue((self.target / "user_code.py").is_file())
        # Managed files removed
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "GEMINI.md").exists())
        # Brain context archived to backup
        backups = list((self.target / ".agents-backups").glob("uninstall_*"))
        self.assertTrue(len(backups) > 0)


if __name__ == "__main__":
    unittest.main()
