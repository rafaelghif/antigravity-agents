#!/usr/bin/env python3
"""
Enterprise Hermes Orchestrator Engine (v5.0.0 L9 Specification)
Deterministic DAG State Machine with Dual-Gate Verification & Crash Checkpointing.
"""
import os
import sys
import time
import json
try:
    import yaml
except ImportError:
    print("Error: 'yaml' module not found. Please install it using: pip install pyyaml", file=sys.stderr)
    sys.exit(1)
import glob
import re
import shlex
import graphlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

TASKS_DIR = Path("tasks")
STATE_DIR = Path(".agents/state")
CHECKPOINT_FILE = STATE_DIR / "checkpoint.json"
BLACKBOARD_SCRIPT = Path("scripts/inbox_manager.py")
VERIFY_SCRIPT = Path("scripts/verify.py")

# Ensure State Directory exists
STATE_DIR.mkdir(parents=True, exist_ok=True)

class EpistemicBlackboard:
    @staticmethod
    def post(sender: str, recipient: str, message: str, evidence: str = "N/A", falsifiability: str = "N/A"):
        if not BLACKBOARD_SCRIPT.exists():
            return
        payload = (
            f"{message}\n"
            f"Evidence_Source: {evidence}\n"
            f"Falsifiability_Criteria: {falsifiability}"
        )
        try:
            subprocess.run(
                [sys.executable, str(BLACKBOARD_SCRIPT), "send", sender, recipient, payload],
                capture_output=True,
                text=True,
                timeout=15
            )
        except Exception as e:
            sys.stderr.write(f"[Blackboard Error] {e}\n")

class StateCheckpoint:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                sys.stderr.write(f"Checkpoint read notice: {e}\n")
        return {
            "completed_tasks": [],
            "in_progress": None,
            "blocked_tasks": [],
            "iterations": {},
            "last_updated": time.time()
        }

    def save(self):
        self.data["last_updated"] = time.time()
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def mark_completed(self, task_id: str):
        if task_id not in self.data["completed_tasks"]:
            self.data["completed_tasks"].append(task_id)
        self.data["in_progress"] = None
        self.save()

    def mark_blocked(self, task_id: str):
        if task_id not in self.data["blocked_tasks"]:
            self.data["blocked_tasks"].append(task_id)
        self.data["in_progress"] = None
        self.save()

    def set_in_progress(self, task_id: str, persona: str, iteration: int):
        self.data["in_progress"] = {
            "task_id": task_id,
            "persona": persona,
            "iteration": iteration,
            "timestamp": time.time()
        }
        self.data["iterations"][task_id] = iteration
        self.save()

    def get_iteration(self, task_id: str) -> int:
        return self.data["iterations"].get(task_id, 1)

class HermesEngine:
    def __init__(self):
        self.checkpoint = StateCheckpoint(CHECKPOINT_FILE)

    def load_task_graph(self) -> Tuple[Dict[str, Dict[str, Any]], graphlib.TopologicalSorter]:
        tasks = {}
        graph = {}

        if not TASKS_DIR.exists():
            return tasks, graphlib.TopologicalSorter({})

        for task_file in sorted(TASKS_DIR.glob("*.yaml")):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if not data or "id" not in data:
                        continue
                    task_id = str(data["id"])
                    data["_file"] = str(task_file)
                    tasks[task_id] = data
                    
                    depends_on = data.get("depends_on", [])
                    if isinstance(depends_on, str):
                        depends_on = [depends_on]
                    graph[task_id] = depends_on
            except Exception as e:
                print(f"[Hermes] Error reading {task_file}: {e}")

        sorter = graphlib.TopologicalSorter(graph)
        try:
            sorter.prepare()
        except graphlib.CycleError as e:
            print(f"❌ [Hermes Fatal] Dependency cycle detected in tasks: {e}")
            sys.exit(1)

        return tasks, sorter

    def update_task_file_status(self, task_file: str, status: str):
        try:
            with open(task_file, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'status:\s*".*?"', f'status: "{status}"', content)
            content = re.sub(r"status:\s*'.*?'", f"status: '{status}'", content)
            with open(task_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[Hermes] Failed to update status in {task_file}: {e}")

    def resolve_persona(self, task_data: Dict[str, Any]) -> str:
        explicit_domain = task_data.get("domain", "").lower()
        if explicit_domain in ["backend", "api", "database", "frontend", "security", "qa"]:
            domain_map = {
                "backend": "staff-backend",
                "api": "staff-backend",
                "frontend": "frontend-architect",
                "ui": "frontend-architect",
                "database": "database-sre",
                "security": "devsecops-principal",
                "qa": "qa-automation-lead"
            }
            if explicit_domain in domain_map:
                return domain_map[explicit_domain]

        text = (task_data.get("title", "") + " " + task_data.get("description", "")).lower()
        if any(k in text for k in ["frontend", "ui", "css", "component", "tailwind", "react"]):
            return "frontend-architect"
        if any(k in text for k in ["database", "schema", "migration", "index", "postgres", "sql"]):
            return "database-sre"
        if any(k in text for k in ["security", "docker", "k8s", "ci/cd", "secret", "guard", "blindfold"]):
            return "devsecops-principal"
        if any(k in text for k in ["test", "fuzz", "qa", "chaos"]):
            return "qa-automation-lead"
        return "staff-backend"

    def _load_persona_skills(self, persona: str) -> str:
        persona_file = Path(f".agents/agents/{persona}.md")
        if not persona_file.exists():
            return ""
        
        skill_texts = []
        try:
            content = persona_file.read_text(encoding="utf-8")
            match = re.search(r"skills:\s*\[(.*?)\]", content)
            if match:
                skill_names = [s.strip() for s in match.group(1).split(",") if s.strip()]
                for sname in skill_names:
                    skill_path = Path(f".agents/skills/{sname}/SKILL.md")
                    if skill_path.exists():
                        skill_texts.append(f"### [SKILL: {sname}]\n{skill_path.read_text(encoding='utf-8')}\n")
        except Exception as e:
            sys.stderr.write(f"Skill loading notice: {e}\n")
            
        return "\n".join(skill_texts)

    def execute_agent(self, persona: str, prompt: str, timeout_seconds: int = 900) -> Tuple[int, str, str]:
        print(f"🤖 [Hermes Dispatcher] Spawning persona '{persona}' (High Reasoning Effort)...")
        cmd = ["agy", "--agent", persona, "--effort", "high", "--dangerously-skip-permissions", "-p", prompt]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            print(f"❌ [Hermes Timeout] Agent '{persona}' exceeded execution limit of {timeout_seconds}s.")
            return -1, "", "TIMEOUT_EXPIRED"
        except Exception as e:
            return -1, "", str(e)

    def evaluate_gate1_static(self) -> Tuple[bool, str]:
        """Gate 1: Deterministic Static AST & Verification Check (0 LLM Tokens)"""
        print("🔍 [Gate 1] Running Deterministic Static Verification...")
        if not VERIFY_SCRIPT.exists():
            return True, "verify.py not found, skipping."

        res = subprocess.run(
            [sys.executable, str(VERIFY_SCRIPT), "--execute", "--terse"],
            capture_output=True,
            text=True,
            timeout=180
        )
        if res.returncode == 0:
            return True, res.stdout
        return False, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

    def evaluate_gate2_cognitive(self, task_data: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        """Gate 2: Cognitive QA Lead Verification & Epistemic Audit"""
        print("🧠 [Gate 2] Dispatching Cognitive QA Reviewer (qa-automation-lead)...")
        task_title = task_data.get("title", "")
        task_desc = task_data.get("description", "")
        acc_criteria = task_data.get("acceptance_criteria", [])
        
        qa_prompt = (
            f"You are the Staff QA Automation Lead. Rigorously review the current codebase and git diff for:\n"
            f"TASK: {task_title}\n"
            f"SPEC: {task_desc}\n"
            f"ACCEPTANCE CRITERIA: {json.dumps(acc_criteria)}\n\n"
            f"Evaluate adherence to L9 Enterprise Standards (tests, edge cases, contracts).\n"
            f"Output ONLY a single valid JSON object strictly matching this schema:\n"
            f"{{\n"
            f'  "status": "APPROVED" | "REJECTED",\n'
            f'  "evidence_source": "<path to test / code verifying condition>",\n'
            f'  "falsifiability_criteria": "<exact condition proving claim false>",\n'
            f'  "feedback": "<actionable remediation directives>"\n'
            f"}}"
        )

        retcode, stdout, stderr = self.execute_agent("qa-automation-lead", qa_prompt, timeout_seconds=300)
        
        # Robust JSON extraction
        try:
            match = re.search(r"\{.*\}", stdout, re.DOTALL)
            if match:
                payload = json.loads(match.group(0))
                status = payload.get("status", "REJECTED").upper()
                evidence = payload.get("evidence_source", "qa_review")
                falsifiability = payload.get("falsifiability_criteria", "code_inspection")
                feedback = payload.get("feedback", "No feedback provided.")
                return (status == "APPROVED"), evidence, falsifiability, feedback
        except Exception as e:
            print(f"[Gate 2 Error] Failed to parse QA output JSON: {e}")

        return False, "qa_parse_failure", "valid_json_output", f"Reviewer output could not be parsed. Raw output:\n{stdout}"

    def run_task_lifecycle(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        task_file = task_data["_file"]
        title = task_data.get("title", task_id)
        desc = task_data.get("description", "")
        persona = self.resolve_persona(task_data)
        
        print(f"\n=======================================================")
        print(f"🚀 [Hermes Task Start] ID: {task_id} | Persona: {persona}")
        print(f"Title: {title}")
        print(f"=======================================================")

        self.update_task_file_status(task_file, "IN_PROGRESS")
        iteration = self.checkpoint.get_iteration(task_id)
        max_iterations = 3
        feedback_context = "Initial task implementation."

        EpistemicBlackboard.post(
            sender="hermes-manager",
            recipient=persona,
            message=f"Dispatched task '{task_id}' to {persona}.",
            evidence=task_file,
            falsifiability=f"Check git status for task {task_id}"
        )

        # Load domain skills dynamically
        injected_skills = self._load_persona_skills(persona)

        while iteration <= max_iterations:
            print(f"\n🔄 [Iteration {iteration}/{max_iterations}] Dispatching Worker...")
            self.checkpoint.set_in_progress(task_id, persona, iteration)

            worker_prompt = (
                f"You are the {persona} (L9 Staff/Principal Engineer).\n"
                f"TASK ID: {task_id}\n"
                f"TITLE: {title}\n"
                f"DESCRIPTION: {desc}\n"
                f"ITERATION: {iteration}/{max_iterations}\n"
                f"FEEDBACK CONTEXT: {feedback_context}\n\n"
                f"================ L9 EXPERT PLAYBOOK & DOMAIN SKILLS ================\n"
                f"{injected_skills}\n"
                f"====================================================================\n\n"
                f"L9 ARCHITECTURAL MANDATES:\n"
                f"1. ZERO JUNIOR CODE: No untyped dicts, no 'any', no bare exceptions, no sham tests.\n"
                f"2. CONTRACT-FIRST: Strict schema validation (DTOs/types) on all boundaries.\n"
                f"3. RESILIENCE: Handle failures, retries with jitter, idempotency, and edge cases.\n"
                f"4. ATOMIC TDD: Write complete unit and boundary tests before finalizing.\n"
                f"5. EXECUTE: Read `.agents/brain/rules.md` and write production code directly."
            )

            ret, stdout, stderr = self.execute_agent(persona, worker_prompt)

            # Gate 1: Deterministic Static Check
            g1_passed, g1_log = self.evaluate_gate1_static()
            if not g1_passed:
                print(f"❌ [Gate 1 FAILED] Static checks violated.")
                feedback_context = f"Gate 1 (Static Analysis / verify.py) FAILED with the following errors:\n{g1_log}\nPlease fix these violations immediately."
                EpistemicBlackboard.post(
                    sender="hermes-gate-1",
                    recipient=persona,
                    message=f"Gate 1 Rejected task {task_id} on iteration {iteration}.",
                    evidence="scripts/verify.py exit code != 0",
                    falsifiability="Run verify.py --execute"
                )
                iteration += 1
                continue

            print("✅ [Gate 1 PASSED] Static verification gates satisfied.")

            # Gate 2: Cognitive QA Lead Check
            g2_approved, evidence, falsifiability, g2_feedback = self.evaluate_gate2_cognitive(task_data)
            if not g2_approved:
                print(f"❌ [Gate 2 REJECTED] QA lead requested changes: {g2_feedback}")
                feedback_context = f"Gate 2 (QA Review) REJECTED your code with the following feedback:\n{g2_feedback}"
                EpistemicBlackboard.post(
                    sender="qa-automation-lead",
                    recipient=persona,
                    message=f"Gate 2 Rejected task {task_id}: {g2_feedback}",
                    evidence=evidence,
                    falsifiability=falsifiability
                )
                iteration += 1
                continue

            # Both Gates Passed!
            print(f"🎉 [Task APPROVED] Task {task_id} successfully verified and approved!")
            self.update_task_file_status(task_file, "DONE")
            self.checkpoint.mark_completed(task_id)
            EpistemicBlackboard.post(
                sender="hermes-manager",
                recipient="@all",
                message=f"Task '{task_id}' verified and marked DONE.",
                evidence=evidence,
                falsifiability=falsifiability
            )
            return True

        # Circuit Breaker Tripped
        print(f"💀 [Circuit Breaker Tripped] Task {task_id} exceeded {max_iterations} iterations without approval.")
        self.update_task_file_status(task_file, "BLOCKED")
        self.checkpoint.mark_blocked(task_id)
        EpistemicBlackboard.post(
            sender="hermes-manager",
            recipient="scrum-master",
            message=f"CIRCUIT BREAKER: Task '{task_id}' blocked after {max_iterations} failed iterations.",
            evidence=f"{task_file} status changed to BLOCKED",
            falsifiability="Check tasks/*.yaml"
        )
        return False

    def _execute_ready_node(self, task_id: str, tasks: Dict[str, Dict[str, Any]], sorter: graphlib.TopologicalSorter) -> bool:
        if task_id in self.checkpoint.data["completed_tasks"]:
            print(f"⏩ [Hermes Checkpoint] Task '{task_id}' already completed. Skipping.")
            sorter.done(task_id)
            return True

        if task_id not in tasks:
            print(f"⚠️ [Hermes Warning] Task '{task_id}' referenced in dependencies but file missing.")
            sorter.done(task_id)
            return True

        task_data = tasks[task_id]
        success = self.run_task_lifecycle(task_id, task_data)
        if success:
            sorter.done(task_id)
            return True
        return False

    def _process_batch(self, ready_tasks: Tuple[str, ...], tasks: Dict[str, Dict[str, Any]], sorter: graphlib.TopologicalSorter) -> bool:
        for task_id in ready_tasks:
            if not self._execute_ready_node(task_id, tasks, sorter):
                print(f"⛔ [Hermes Halted] Dependency node '{task_id}' failed. Downstream tasks halted.")
                return False
        return True

    def run(self):
        print("==============================================================")
        print("🌟 Enterprise Hermes Autonomous Orchestrator v5.0.0")
        print("==============================================================")

        tasks, sorter = self.load_task_graph()
        if not tasks:
            print("💤 No tasks found in 'tasks/' directory. Hermes is idling.")
            return

        while sorter.is_active():
            ready_tasks = sorter.get_ready()
            if not ready_tasks:
                print("💤 No ready tasks available (waiting on predecessors).")
                break

            if not self._process_batch(ready_tasks, tasks, sorter):
                return

        print("\n✨ [Hermes Complete] All DAG workflow tasks have been processed.")

if __name__ == "__main__":
    HermesEngine().run()
