import sys
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import intent_compiler

class TestIntentCompiler(unittest.TestCase):
    def test_valid_intent_compiles(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
            tf.write('name: "Test System"\nstatus: "DONE"\ndescription: "A valid system intent"\n')
            temp_name = tf.name
        try:
            success = intent_compiler.compile_intent(temp_name)
            self.assertTrue(success)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def test_missing_required_fields_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
            tf.write('description: "Missing name and status"\n')
            temp_name = tf.name
        try:
            success = intent_compiler.compile_intent(temp_name)
            self.assertFalse(success)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def test_invalid_status_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
            tf.write('name: "Invalid"\nstatus: "PENDING"\n')
            temp_name = tf.name
        try:
            success = intent_compiler.compile_intent(temp_name)
            self.assertFalse(success)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def test_non_existent_file_fails(self):
        success = intent_compiler.compile_intent("/non/existent/intent.yaml")
        self.assertFalse(success)

    def test_infer_task_domain(self):
        self.assertEqual(intent_compiler.infer_task_domain("Create postgres migration for users"), ("database", "database-sre"))
        self.assertEqual(intent_compiler.infer_task_domain("Build tailwind UI modal component"), ("frontend", "frontend-architect"))
        self.assertEqual(intent_compiler.infer_task_domain("Setup docker container and rbac security"), ("security", "devsecops-principal"))
        self.assertEqual(intent_compiler.infer_task_domain("Execute chaos fuzz testing suite"), ("qa", "qa-automation-lead"))
        self.assertEqual(intent_compiler.infer_task_domain("Implement gRPC order service endpoint"), ("backend", "staff-backend"))

    def test_slugify(self):
        self.assertEqual(intent_compiler.slugify("Implement a daemon (`scripts/autonomous_loop.py`)"), "implement_a_daemon_scripts")
        self.assertEqual(intent_compiler.slugify("!@#$% Special   Chars ???"), "special_chars")
        self.assertEqual(intent_compiler.slugify(""), "task")

    def test_decompose_intent_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            intent_file = Path(tmp_dir) / "intent.yaml"
            tasks_out = Path(tmp_dir) / "tasks"
            intent_file.write_text(
                'name: "Ecommerce"\nstatus: "IN_PROGRESS"\nobjectives:\n'
                '  - "Database schema and postgres migration for orders"\n'
                '  - "REST API endpoints for checkout"\n'
                '  - "React frontend checkout form component"\n'
                '  - "End-to-end integration tests and load testing"\n',
                encoding="utf-8"
            )
            created = intent_compiler.decompose_intent(str(intent_file), output_dir=tasks_out)
            self.assertEqual(len(created), 4)

            # Check personas and dependencies
            t1 = tasks_out / "01_database_schema_and_postgres.yaml"
            t2 = tasks_out / "02_rest_api_endpoints_for.yaml"
            t3 = tasks_out / "03_react_frontend_checkout_form.yaml"
            t4 = tasks_out / "04_end_to_end_integration.yaml"

            self.assertTrue(t1.exists())
            self.assertTrue(t2.exists())
            self.assertTrue(t3.exists())
            self.assertTrue(t4.exists())

            t1_text = t1.read_text(encoding="utf-8")
            self.assertIn('assigned_persona: "database-sre"', t1_text)
            self.assertIn("depends_on: []", t1_text)

            t2_text = t2.read_text(encoding="utf-8")
            self.assertIn('assigned_persona: "staff-backend"', t2_text)
            self.assertIn('- "01_database_schema_and_postgres"', t2_text)

            t3_text = t3.read_text(encoding="utf-8")
            self.assertIn('assigned_persona: "frontend-architect"', t3_text)
            self.assertIn('- "02_rest_api_endpoints_for"', t3_text)

            t4_text = t4.read_text(encoding="utf-8")
            self.assertIn('assigned_persona: "qa-automation-lead"', t4_text)
            self.assertIn('- "03_react_frontend_checkout_form"', t4_text)

    def test_decompose_intent_skips_done_unless_force(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            intent_file = Path(tmp_dir) / "intent.yaml"
            tasks_out = Path(tmp_dir) / "tasks"
            intent_file.write_text(
                'name: "App"\nstatus: "IN_PROGRESS"\nobjectives:\n  - "Task one"\n',
                encoding="utf-8"
            )
            created = intent_compiler.decompose_intent(str(intent_file), output_dir=tasks_out)
            t1 = created[0]
            # Mark it done with custom content
            t1.write_text('id: "01_task_one"\nstatus: "DONE"\ncustom_field: true\n', encoding="utf-8")

            # Run again without force
            intent_compiler.decompose_intent(str(intent_file), output_dir=tasks_out, force=False)
            self.assertIn("custom_field: true", t1.read_text(encoding="utf-8"))

            # Run again with force
            intent_compiler.decompose_intent(str(intent_file), output_dir=tasks_out, force=True)
            self.assertNotIn("custom_field: true", t1.read_text(encoding="utf-8"))
            self.assertIn('status: "PENDING"', t1.read_text(encoding="utf-8"))

    def test_decompose_empty_objectives(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            intent_file = Path(tmp_dir) / "intent.yaml"
            intent_file.write_text('name: "App"\nstatus: "IN_PROGRESS"\n', encoding="utf-8")
            created = intent_compiler.decompose_intent(str(intent_file), output_dir=Path(tmp_dir) / "tasks")
            self.assertEqual(created, [])

if __name__ == "__main__":
    unittest.main()
