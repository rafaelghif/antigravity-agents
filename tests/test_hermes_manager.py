import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.hermes_manager import HermesEngine, StateCheckpoint

class TestHermesManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.checkpoint_file = Path(self.tmp_dir.name) / "checkpoint.json"
        self.checkpoint = StateCheckpoint(self.checkpoint_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_checkpoint_lifecycle(self):
        self.assertEqual(len(self.checkpoint.data["completed_tasks"]), 0)
        self.checkpoint.mark_completed("TASK-101")
        self.assertIn("TASK-101", self.checkpoint.data["completed_tasks"])
        self.assertIsNone(self.checkpoint.data["in_progress"])

        self.checkpoint.set_in_progress("TASK-102", "staff-backend", 1)
        self.assertIsNotNone(self.checkpoint.data["in_progress"])
        self.assertEqual(self.checkpoint.data["in_progress"]["task_id"], "TASK-102")

        self.checkpoint.mark_blocked("TASK-102")
        self.assertIn("TASK-102", self.checkpoint.data["blocked_tasks"])
        self.assertIsNone(self.checkpoint.data["in_progress"])

    def test_reconcile_checkpoint_clears_zombie_task(self):
        engine = HermesEngine()
        engine.checkpoint = self.checkpoint
        self.checkpoint.set_in_progress("01_test_task", "staff-backend", 1)
        tasks_dir = Path(self.tmp_dir.name) / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "01_test_task.yaml").write_text("id: '01_test_task'\nstatus: 'DONE'\n", encoding="utf-8")
        with patch("scripts.hermes_manager.TASKS_DIR", tasks_dir):
            engine.reconcile_checkpoint()
            self.assertIn("01_test_task", self.checkpoint.data["completed_tasks"])
            self.assertIsNone(self.checkpoint.data["in_progress"])

    def test_resolve_persona_explicit_domain(self):
        engine = HermesEngine()
        self.assertEqual(engine.resolve_persona({"domain": "frontend"}), "frontend-architect")
        self.assertEqual(engine.resolve_persona({"domain": "ui"}), "frontend-architect")
        self.assertEqual(engine.resolve_persona({"domain": "database"}), "database-sre")
        self.assertEqual(engine.resolve_persona({"domain": "security"}), "devsecops-principal")
        self.assertEqual(engine.resolve_persona({"domain": "qa"}), "qa-automation-lead")
        self.assertEqual(engine.resolve_persona({"domain": "backend"}), "staff-backend")
        self.assertEqual(engine.resolve_persona({"domain": "product"}), "product-manager")
        self.assertEqual(engine.resolve_persona({"domain": "research"}), "researcher")
        self.assertEqual(engine.resolve_persona({"domain": "scrum"}), "scrum-master")

    def test_resolve_persona_inferred_from_title(self):
        engine = HermesEngine()
        self.assertEqual(engine.resolve_persona({"title": "Create react modal component"}), "frontend-architect")
        self.assertEqual(engine.resolve_persona({"title": "Add postgres migration for users"}), "database-sre")
        self.assertEqual(engine.resolve_persona({"title": "Fix docker container secret scanning"}), "devsecops-principal")
        self.assertEqual(engine.resolve_persona({"title": "Fuzz testing boundary conditions"}), "qa-automation-lead")
        self.assertEqual(engine.resolve_persona({"title": "Draft PRD and user story breakdown"}), "product-manager")
        self.assertEqual(engine.resolve_persona({"title": "Research state of the art papers on diffusion"}), "researcher")

    def test_resolve_persona_assigned_priority(self):
        engine = HermesEngine()
        self.assertEqual(engine.resolve_persona({"assigned_persona": "database-sre", "domain": "backend"}), "database-sre")
        self.assertEqual(engine.resolve_persona({"assigned_persona": "custom-agent"}), "custom-agent")

    def test_load_persona_skills_multiline_yaml(self):
        engine = HermesEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            agent_dir = tmproot / ".agents" / "agents"
            agent_dir.mkdir(parents=True)
            skills_dir = tmproot / ".agents" / "skills" / "architecture"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# Architecture Skill\n")
            (agent_dir / "custom-agent.md").write_text("""---
name: custom-agent
skills:
  - architecture
---
Body
""")
            with patch("scripts.hermes_manager.ROOT", tmproot):
                loaded = engine._load_persona_skills("custom-agent")
                self.assertIn("Architecture Skill", loaded)

    def test_execute_agent_fallback_when_no_agy(self):
        engine = HermesEngine()
        with patch("shutil.which", return_value=None), \
             patch("scripts.hermes_manager.EpistemicBlackboard.post") as mock_post:
            retcode, stdout, stderr = engine.execute_agent("staff-backend", "Write auth controller")
            self.assertEqual(retcode, 0)
            self.assertIn("APPROVED", stdout)
            mock_post.assert_called_once()

    def test_execute_agent_passes_model_flags(self):
        engine = HermesEngine()
        with patch("shutil.which", return_value="/usr/local/bin/agy"), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
            engine.execute_agent("staff-backend", "Implement feature")
            called_cmd = mock_run.call_args[0][0]
            self.assertIn("--model", called_cmd)
            self.assertIn("gemini-3.1-pro-high", called_cmd)
            self.assertIn("--effort", called_cmd)
            self.assertIn("high", called_cmd)

            engine.execute_agent("scrum-master", "Plan sprint")
            called_cmd2 = mock_run.call_args[0][0]
            self.assertIn("--model", called_cmd2)
            self.assertIn("gemini-3.8-flash-high", called_cmd2)
            self.assertIn("--effort", called_cmd2)
            self.assertIn("high", called_cmd2)

    def test_execute_agent_upgrades_reduced_effort_and_preserves_pro(self):
        engine = HermesEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            agents_dir = tmproot / ".agents" / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            # Create an agent file with explicit low effort
            (agents_dir / "low-effort-agent.md").write_text(
                "---\nname: low-effort-agent\nmodel: flash\neffort: low\n---\nBody\n",
                encoding="utf-8"
            )
            # Create an agent file with full pro model name
            (agents_dir / "full-pro-agent.md").write_text(
                "---\nname: full-pro-agent\nmodel: gemini-3.1-pro-high\neffort: medium\n---\nBody\n",
                encoding="utf-8"
            )

            with patch("scripts.hermes_manager.ROOT", tmproot), \
                 patch("shutil.which", return_value="/usr/local/bin/agy"), \
                 patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
                
                # Low effort must be upgraded to high and use gemini-3.8-flash-high
                engine.execute_agent("low-effort-agent", "Do task")
                cmd1 = mock_run.call_args[0][0]
                self.assertIn("gemini-3.8-flash-high", cmd1)
                self.assertIn("high", cmd1)
                self.assertNotIn("low", cmd1)

                # Full pro model name must be preserved with gemini-3.1-pro-high and high effort
                engine.execute_agent("full-pro-agent", "Do pro task")
                cmd2 = mock_run.call_args[0][0]
                self.assertIn("gemini-3.1-pro-high", cmd2)
                self.assertIn("high", cmd2)
                self.assertNotIn("medium", cmd2)

    def test_evaluate_gate2_cognitive_fallback(self):
        engine = HermesEngine()
        with patch("shutil.which", return_value=None):
            approved, evidence, falsifiability, feedback = engine.evaluate_gate2_cognitive({"title": "Test task"})
            self.assertTrue(approved)
            self.assertIsInstance(evidence, str)
            self.assertIsInstance(feedback, str)

    def test_compute_execution_plan_waves(self):
        engine = HermesEngine()
        mock_tasks = {
            "01_db": {"id": "01_db", "title": "DB Init", "domain": "database", "depends_on": []},
            "02_api": {"id": "02_api", "title": "API Backend", "domain": "backend", "depends_on": ["01_db"]},
            "03_fe": {"id": "03_fe", "title": "Frontend UI", "domain": "frontend", "depends_on": ["02_api"]},
            "04_qa": {"id": "04_qa", "title": "QA Tests", "domain": "qa", "depends_on": ["02_api"]},
        }
        with patch.object(engine, "load_task_graph", return_value=(mock_tasks, None)):
            plan = engine.compute_execution_plan()
            self.assertEqual(plan["total_tasks"], 4)
            self.assertEqual(plan["total_waves"], 3)
            self.assertEqual(plan["max_concurrency"], 2)

            wave1 = [t["id"] for t in plan["waves"][0]]
            wave2 = [t["id"] for t in plan["waves"][1]]
            wave3 = sorted([t["id"] for t in plan["waves"][2]])

            self.assertEqual(wave1, ["01_db"])
            self.assertEqual(wave2, ["02_api"])
            self.assertEqual(wave3, ["03_fe", "04_qa"])

    def test_generate_mermaid_graph(self):
        engine = HermesEngine()
        mock_tasks = {
            "01_db": {"id": "01_db", "title": "DB Init", "domain": "database", "depends_on": []},
            "02_api": {"id": "02_api", "title": "API Backend", "domain": "backend", "depends_on": ["01_db"]},
        }
        plan = {"tasks": mock_tasks}
        mermaid_out = engine.generate_mermaid_graph(plan)
        self.assertIn("graph TD", mermaid_out)
        self.assertIn('01_db["01_db (database-sre)"]', mermaid_out)
        self.assertIn("01_db --> 02_api", mermaid_out)

    def test_print_plan_json(self):
        import io
        engine = HermesEngine()
        mock_tasks = {
            "01_db": {"id": "01_db", "title": "DB Init", "domain": "database", "depends_on": []}
        }
        with patch.object(engine, "load_task_graph", return_value=(mock_tasks, None)), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            engine.print_plan(as_json=True)
            output = json.loads(mock_stdout.getvalue())
            self.assertEqual(output["total_tasks"], 1)
            self.assertEqual(output["total_waves"], 1)

    def test_print_plan_mermaid_text(self):
        import io
        engine = HermesEngine()
        mock_tasks = {
            "01_db": {"id": "01_db", "title": "DB Init", "domain": "database", "depends_on": []}
        }
        with patch.object(engine, "load_task_graph", return_value=(mock_tasks, None)), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            engine.print_plan(as_json=False, mermaid=True)
            val = mock_stdout.getvalue()
            self.assertIn("Hermes DAG Execution Plan", val)
            self.assertIn("```mermaid", val)

    def test_worker_prompt_clarifies_rules_distinction(self):
        engine = HermesEngine()
        engine.checkpoint = self.checkpoint
        task_data = {
            "id": "task_prompt_test",
            "title": "Prompt Test",
            "description": "Verify worker prompt contains rules distinction",
            "domain": "backend",
            "_file": Path("/tmp/fake_task.yaml"),
        }
        captured_prompts = []
        def mock_execute_agent(persona, prompt):
            captured_prompts.append(prompt)
            return 0, "APPROVED", ""

        import io
        with patch.object(engine, "update_task_file_status"), \
             patch.object(engine, "execute_agent", side_effect=mock_execute_agent), \
             patch.object(engine, "evaluate_gate1_static", return_value=(True, "OK")), \
             patch.object(engine, "evaluate_gate2_cognitive", return_value=(True, "OK", "falsify", "approved")), \
             patch("sys.stdout", new_callable=io.StringIO):
            engine.run_task_lifecycle("task_prompt_test", task_data)

        self.assertTrue(len(captured_prompts) > 0)
        self.assertIn("Read `.agents/rules/` for immutable platform rules and `.agents/brain/rules.md` for dynamic multi-agent coordination contracts", captured_prompts[0])

if __name__ == "__main__":
    unittest.main()
