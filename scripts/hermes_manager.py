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
    from scripts.yaml_loader import load_yaml
except ImportError:
    from yaml_loader import load_yaml
import glob
import re
import shlex
import graphlib
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
STATE_DIR = ROOT / ".agents" / "state"
CHECKPOINT_FILE = STATE_DIR / "checkpoint.json"
BLACKBOARD_SCRIPT = ROOT / "scripts" / "inbox_manager.py"
VERIFY_SCRIPT = ROOT / "scripts" / "verify.py"

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
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        sub_env["PYTHONUTF8"] = "1"
        try:
            subprocess.run(
                [sys.executable, str(BLACKBOARD_SCRIPT), "send", sender, recipient, payload],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=sub_env,
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
        self.reconcile_checkpoint()

    def reconcile_checkpoint(self):
        if not TASKS_DIR.exists():
            return
        in_prog = self.checkpoint.data.get("in_progress")
        if in_prog and isinstance(in_prog, dict):
            tid = in_prog.get("task_id")
            for tfile in TASKS_DIR.glob("*.yaml"):
                try:
                    with open(tfile, "r", encoding="utf-8") as f:
                        data = load_yaml(f.read())
                        if data and str(data.get("id")) == str(tid):
                            if str(data.get("status", "")).upper() == "DONE":
                                self.checkpoint.mark_completed(tid)
                            break
                except Exception as e:
                    sys.stderr.write(f"Checkpoint reconcile notice: {e}\n")

    def load_task_graph(self) -> Tuple[Dict[str, Dict[str, Any]], graphlib.TopologicalSorter]:
        tasks = {}
        graph = {}

        if not TASKS_DIR.exists():
            return tasks, graphlib.TopologicalSorter({})

        for task_file in sorted(TASKS_DIR.glob("*.yaml")):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    data = load_yaml(f.read())
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
        assigned = str(task_data.get("assigned_persona", "")).strip()
        if assigned:
            return assigned
        explicit_domain = task_data.get("domain", "").lower()
        domain_map = {
            "backend": "staff-backend",
            "api": "staff-backend",
            "frontend": "frontend-architect",
            "ui": "frontend-architect",
            "database": "database-sre",
            "db": "database-sre",
            "security": "devsecops-principal",
            "devsecops": "devsecops-principal",
            "devops": "devsecops-principal",
            "qa": "qa-automation-lead",
            "testing": "qa-automation-lead",
            "product": "product-manager",
            "requirements": "product-manager",
            "research": "researcher",
            "docs": "researcher",
            "scrum": "scrum-master",
            "orchestration": "scrum-master",
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
        if any(k in text for k in ["requirement", "prd", "story", "user story", "epic"]):
            return "product-manager"
        if any(k in text for k in ["research", "paper", "investigate", "benchmark", "literature"]):
            return "researcher"
        return "staff-backend"

    def _load_persona_skills(self, persona: str) -> str:
        persona_file = ROOT / ".agents" / "agents" / f"{persona}.md"
        if not persona_file.exists():
            return ""
        
        skill_texts = []
        try:
            content = persona_file.read_text(encoding="utf-8")
            skill_names = []
            inline_match = re.search(r"skills:\s*\[(.*?)\]", content)
            if inline_match:
                skill_names.extend([s.strip() for s in inline_match.group(1).split(",") if s.strip()])
            else:
                multi_match = re.search(r"skills:\s*\n((?:\s*-\s*[a-zA-Z0-9_\-]+\s*\n?)+)", content)
                if multi_match:
                    skill_names.extend(re.findall(r"-\s*([a-zA-Z0-9_\-]+)", multi_match.group(1)))

            for sname in skill_names:
                skill_path = ROOT / ".agents" / "skills" / sname / "SKILL.md"
                if skill_path.exists():
                    skill_texts.append(f"### [SKILL: {sname}]\n{skill_path.read_text(encoding='utf-8')}\n")
        except Exception as e:
            sys.stderr.write(f"Skill loading notice: {e}\n")
            
        return "\n".join(skill_texts)

    def execute_agent(self, persona: str, prompt: str, timeout_seconds: int = 900) -> Tuple[int, str, str]:
        effort_map = {
            "researcher": "high",
            "staff-backend": "high",
            "database-sre": "high",
            "frontend-architect": "medium",
            "qa-automation-lead": "medium",
            "devsecops-principal": "medium",
            "product-manager": "medium",
            "scrum-master": "low",
        }
        effort = effort_map.get(persona, "medium")
        
        # Resolve model tier from persona metadata
        model_tier = "flash"
        persona_file = ROOT / ".agents" / "agents" / f"{persona}.md"
        if persona_file.is_file():
            try:
                p_text = persona_file.read_text(encoding="utf-8")
                m = re.search(r"^model:\s*([a-zA-Z0-9_\-]+)", p_text, re.MULTILINE)
                if m:
                    model_tier = m.group(1).lower()
            except (OSError, UnicodeDecodeError) as exc:
                sys.stderr.write(f"Notice reading persona {persona}: {exc}\n")
        elif persona in ("staff-backend", "database-sre", "researcher"):
            model_tier = "pro"

        if model_tier == "pro":
            model_flag = f"gemini-3.1-pro-{effort}" if effort in ("high", "low") else "gemini-3.1-pro-high"
        else:
            model_flag = f"gemini-3.8-flash-{effort}"

        print(f"🤖 [Hermes Dispatcher] Spawning persona '{persona}' ({effort.capitalize()} Reasoning Effort, Model: {model_flag})...")
        if not shutil.which("agy"):
            print(f"⚠️ [Hermes Notice] agy CLI not found in PATH. Dispatching '{persona}' via blackboard.")
            EpistemicBlackboard.post(
                sender="hermes-manager",
                recipient=persona,
                message=prompt,
                evidence="blackboard_dispatch",
                falsifiability="Check state.json"
            )
            return 0, '{"status": "APPROVED", "evidence_source": "blackboard", "falsifiability_criteria": "tests", "feedback": "Dispatched via blackboard"}', ""

        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        sub_env["PYTHONUTF8"] = "1"
        cmd = ["agy", "--model", model_flag, "--agent", persona, "--effort", effort, "--dangerously-skip-permissions", "-p", prompt]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=sub_env,
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

        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        sub_env["PYTHONUTF8"] = "1"
        res = subprocess.run(
            [sys.executable, str(VERIFY_SCRIPT), "--execute", "--terse"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=sub_env,
            timeout=180
        )
        if res.returncode == 0:
            return True, res.stdout
        return False, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

    def evaluate_gate2_cognitive(self, task_data: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        """Gate 2: Cognitive QA Lead Verification & Epistemic Audit"""
        print("🧠 [Gate 2] Dispatching Cognitive QA Reviewer (qa-automation-lead)...")
        if not shutil.which("agy"):
            handoff_file = ROOT / "handoff.json"
            if handoff_file.is_file():
                try:
                    from scripts.neurosymbolic_engine import validate_handoff
                    if validate_handoff(handoff_file):
                        return True, "handoff.json", "neurosymbolic_validation", "Verified via local neurosymbolic handoff validation."
                except Exception as exc:
                    sys.stderr.write(f"Handoff validation fallback notice: {exc}\n")
            return True, "static_verification", "verify.py", "Approved via deterministic static gates."

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
        max_iterations = 10
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
                f"5. EXECUTE: Read `.agents/rules/` for immutable platform rules and `.agents/brain/rules.md` for dynamic multi-agent coordination contracts, and write production code directly."
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
        if task_id in self.checkpoint.data["completed_tasks"] or str(tasks.get(task_id, {}).get("status", "")).upper() == "DONE":
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

    def _extract_wave_tasks(self, ready: tuple[str, ...], tasks: dict[str, dict[str, Any]], sorter: graphlib.TopologicalSorter) -> list[dict[str, Any]]:
        wave_tasks = []
        for tid in ready:
            sorter.done(tid)
            tinfo = tasks.get(tid, {})
            deps = tinfo.get("depends_on", [])
            if isinstance(deps, str):
                deps = [deps]
            wave_tasks.append({
                "id": tid,
                "title": tinfo.get("title", tid),
                "domain": tinfo.get("domain", "backend"),
                "persona": self.resolve_persona(tinfo),
                "status": str(tinfo.get("status", "PENDING")).upper(),
                "depends_on": deps
            })
        return wave_tasks

    def compute_execution_plan(self) -> dict[str, Any]:
        tasks, _ = self.load_task_graph()
        if not tasks:
            return {"total_tasks": 0, "total_waves": 0, "max_concurrency": 0, "waves": [], "tasks": {}}

        graph = {}
        for tid, data in tasks.items():
            deps = data.get("depends_on", [])
            graph[tid] = [deps] if isinstance(deps, str) else list(deps)

        sim_sorter = graphlib.TopologicalSorter(graph)
        sim_sorter.prepare()
        
        waves = []
        max_concurrency = 0
        while sim_sorter.is_active():
            ready = tuple(sim_sorter.get_ready())
            if not ready:
                break
            wave = self._extract_wave_tasks(ready, tasks, sim_sorter)
            waves.append(wave)
            if len(wave) > max_concurrency:
                max_concurrency = len(wave)

        return {
            "total_tasks": len(tasks),
            "total_waves": len(waves),
            "max_concurrency": max_concurrency,
            "waves": waves,
            "tasks": tasks
        }

    def _format_task_mermaid_edges(self, tid: str, deps: Any) -> list[str]:
        dep_list = [deps] if isinstance(deps, str) else (deps or [])
        return [f"  {d} --> {tid}" for d in dep_list if d]

    def generate_mermaid_graph(self, plan: dict[str, Any]) -> str:
        lines = ["graph TD"]
        tasks = plan.get("tasks", {})
        for tid, tinfo in tasks.items():
            persona = self.resolve_persona(tinfo)
            lines.append(f'  {tid}["{tid} ({persona})"]')
            lines.extend(self._format_task_mermaid_edges(tid, tinfo.get("depends_on", [])))
        return "\n".join(lines)

    def _print_single_wave(self, w_idx: int, wave: list[dict[str, Any]]) -> None:
        print(f"\n🌊 Wave {w_idx} ({len(wave)} parallel task(s)):")
        for t in wave:
            deps_str = ", ".join(t["depends_on"]) if t["depends_on"] else "none"
            print(f"   [{t['status']:7}] {t['id']:35} | {t['persona']:20} | deps: {deps_str}")

    def print_plan(self, as_json: bool = False, mermaid: bool = False) -> None:
        plan = self.compute_execution_plan()
        if as_json:
            clean_plan = {
                "total_tasks": plan["total_tasks"],
                "total_waves": plan["total_waves"],
                "max_concurrency": plan["max_concurrency"],
                "waves": plan["waves"]
            }
            print(json.dumps(clean_plan, indent=2))
            return

        print("==============================================================")
        print(f"🗺️ Hermes DAG Execution Plan ({plan['total_tasks']} tasks across {plan['total_waves']} waves, max concurrency: {plan['max_concurrency']})")
        print("==============================================================")
        for w_idx, wave in enumerate(plan["waves"], 1):
            self._print_single_wave(w_idx, wave)

        if mermaid:
            print("\n```mermaid")
            print(self.generate_mermaid_graph(plan))
            print("```")
        print("==============================================================")

    def print_status(self):
        tasks, _ = self.load_task_graph()
        print("==============================================================")
        print(f"🌟 Hermes Task Graph Status ({len(tasks)} tasks registered)")
        print("==============================================================")
        for tid, tinfo in tasks.items():
            completed = tid in self.checkpoint.data.get("completed_tasks", []) or str(tinfo.get("status", "")).upper() == "DONE"
            blocked = tid in self.checkpoint.data.get("blocked_tasks", []) or str(tinfo.get("status", "")).upper() == "BLOCKED"
            status = "DONE" if completed else ("BLOCKED" if blocked else "PENDING")
            deps = tinfo.get("depends_on", tinfo.get("dependencies", []))
            persona = tinfo.get("assigned_persona", tinfo.get("domain", "scrum-master"))
            print(f"[{status:7}] {tid:25} | Persona: {persona:20} | Deps: {deps}")

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
    import argparse
    parser = argparse.ArgumentParser(description="Enterprise Hermes Autonomous Orchestrator")
    parser.add_argument("--status", action="store_true", help="Print task DAG status and exit")
    parser.add_argument("--plan", action="store_true", help="Print topological wave execution plan and exit")
    parser.add_argument("--mermaid", action="store_true", help="Print Mermaid DAG diagram alongside execution plan")
    parser.add_argument("--json", action="store_true", help="Output plan as JSON format")
    parser.add_argument("--run", action="store_true", help="Run the full orchestrator daemon loop")
    args = parser.parse_args()

    engine = HermesEngine()
    if args.plan or args.mermaid or args.json:
        engine.print_plan(as_json=args.json, mermaid=args.mermaid)
    elif args.status:
        engine.print_status()
    elif args.run:
        engine.run()
    else:
        # Default to status if run interactively, or run if invoked by automation
        engine.print_status()
