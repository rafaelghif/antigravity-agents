import sys
import unittest
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import dag_orchestrator

class TestDagOrchestrator(unittest.TestCase):
    def test_check_can_run_dependencies(self):
        graph = {"task_b": ["task_a"], "task_c": ["task_a", "task_b"]}
        results = {"task_a": True, "task_b": True}
        self.assertTrue(dag_orchestrator.check_can_run("task_b", graph, results))
        self.assertTrue(dag_orchestrator.check_can_run("task_c", graph, results))

        results_failed = {"task_a": True, "task_b": False}
        self.assertFalse(dag_orchestrator.check_can_run("task_c", graph, results_failed))

    def test_run_task_success(self):
        task_info = {"command": f'"{sys.executable}" -c "print(\'dag ok\')"', "timeout": 10}
        success = asyncio.run(dag_orchestrator.run_task("test_success", task_info))
        self.assertTrue(success)

    def test_run_task_failure(self):
        task_info = {"command": f'"{sys.executable}" -c "import sys; sys.exit(1)"', "timeout": 10}
        success = asyncio.run(dag_orchestrator.run_task("test_fail", task_info))
        self.assertFalse(success)

    def test_run_task_empty_command(self):
        task_info = {"command": ""}
        success = asyncio.run(dag_orchestrator.run_task("test_empty", task_info))
        self.assertFalse(success)

    def test_run_task_python_interpreter_substitution(self):
        task_info = {"command": "python3 -c \"print('hello')\"", "timeout": 10}
        success = asyncio.run(dag_orchestrator.run_task("test_subst", task_info))
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
