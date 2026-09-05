import asyncio
import graphlib
try:
    from scripts.yaml_loader import load_yaml
except ImportError:
    from yaml_loader import load_yaml
import sys
import os
import argparse
from pathlib import Path
import shlex

ROOT = Path(__file__).resolve().parents[1]

async def run_task(task_id: str, task_info: dict) -> bool:
    command = task_info.get("command", "")
    if not command:
        print(f"[{task_id}] No command specified.")
        return False
    
    print(f"[{task_id}] Starting: {command}")
    is_win = sys.platform == "win32"
    cmd_parts = shlex.split(command, posix=not is_win)
    if is_win:
        cmd_parts = [p.strip('"') for p in cmd_parts]
    if cmd_parts and cmd_parts[0] in ("python", "python3", "py"):
        cmd_parts[0] = sys.executable
    
    timeout_sec = float(task_info.get("timeout", 300))
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ROOT),
            env=sub_env
        )
    except Exception as exc:
        print(f"[{task_id}] Process launch failed: {exc}")
        return False
    
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        print(f"[{task_id}] Timed out after {timeout_sec}s. Terminating...")
        try:
            process.kill()
            await process.wait()
        except Exception as k_err:
            sys.stderr.write(f"Kill notice: {k_err}\n")
        return False
    
    if process.returncode == 0:
        print(f"[{task_id}] Completed successfully.")
        return True
    else:
        print(f"[{task_id}] Failed with code {process.returncode}.")
        if stdout:
            print(f"[{task_id}] STDOUT: {stdout.decode('utf-8', errors='replace').strip()}")
        if stderr:
            print(f"[{task_id}] STDERR: {stderr.decode('utf-8', errors='replace').strip()}")
        return False

def check_can_run(node: str, graph: dict, results: dict) -> bool:
    preds = graph[node]
    successful_preds = [p for p in preds if results.get(p, False)]
    return len(preds) == len(successful_preds)

def process_ready_nodes(ready_nodes: tuple, graph: dict, results: dict, ts: graphlib.TopologicalSorter, running_tasks: set, worker: object) -> None:
    for node in ready_nodes:
        if check_can_run(node, graph, results):
            task = asyncio.create_task(worker(node))
            running_tasks.add(task)
        else:
            print(f"[{node}] Skipped due to predecessor failure.")
            results[node] = False
            ts.done(node)

def process_done_tasks(done: set, results: dict, ts: graphlib.TopologicalSorter) -> None:
    for task in done:
        task_id, success = task.result()
        results[task_id] = success
        ts.done(task_id)

async def main():
    parser = argparse.ArgumentParser(description="DAG Orchestrator")
    parser.add_argument("workflow_file", type=str, help="Path to workflow YAML file")
    args = parser.parse_args()

    workflow_path = Path(args.workflow_file)
    if not workflow_path.exists():
        print(f"Error: {workflow_path} not found.")
        sys.exit(1)

    with open(workflow_path, 'r', encoding='utf-8') as f:
        try:
            workflow = load_yaml(f.read())
        except Exception as e:
            print(f"Error parsing YAML: {e}")
            sys.exit(1)

    tasks = workflow.get("tasks", {})
    if not tasks:
        print("No tasks found in workflow.")
        sys.exit(1)

    graph = {}
    for task_id, task_info in tasks.items():
        depends_on = task_info.get("depends_on", [])
        graph[task_id] = depends_on

    try:
        ts = graphlib.TopologicalSorter(graph)
        ts.prepare()
    except graphlib.CycleError as e:
        print(f"Error: Cycle detected in workflow dependencies - {e}")
        sys.exit(1)

    results = {}
    running_tasks = set()

    async def worker(task_id):
        success = await run_task(task_id, tasks[task_id])
        return task_id, success

    while ts.is_active():
        ready_nodes = ts.get_ready()
        
        if ready_nodes:
            process_ready_nodes(ready_nodes, graph, results, ts, running_tasks, worker)
        
        if running_tasks:
            done, pending = await asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED)
            running_tasks = pending
            process_done_tasks(done, results, ts)

    overall_success = all(results.values())
    if overall_success:
        print("Workflow completed successfully.")
        sys.exit(0)
    else:
        print("Workflow completed with errors.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
