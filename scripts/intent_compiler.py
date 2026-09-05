#!/usr/bin/env python3
"""
Strict Intent Compiler & Auto-Decomposition Engine (v5.0.0 L9 Specification)
Compiles intent.yaml into JSON blackboard artifact and auto-decomposes objectives
into topologically-ordered, persona-routed micro-tasks.
"""
from __future__ import annotations
import sys
try:
    from scripts.yaml_loader import load_yaml
except ImportError:
    from yaml_loader import load_yaml
import json
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]

def infer_task_domain(text: str) -> Tuple[str, str]:
    """Infers (domain, assigned_persona) from objective text."""
    low = text.lower()
    if re.search(r"\b(database|migration|schema|sql|index|postgres|sqlite|table|ddl)\b", low):
        return "database", "database-sre"
    if re.search(r"\b(security|docker|k8s|kubernetes|secret|rbac|ci/cd|pipeline|auth)\b", low):
        return "security", "devsecops-principal"
    if re.search(r"\b(test|tests|testing|fuzz|qa|chaos|e2e|acceptance|audit|coverage)\b", low):
        return "qa", "qa-automation-lead"
    if re.search(r"\b(frontend|ui|component|css|tailwind|react|vue|html|wcag|a11y)\b", low):
        return "frontend", "frontend-architect"
    return "backend", "staff-backend"

def slugify(text: str, max_words: int = 4) -> str:
    """Creates a clean filesystem slug from objective text."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text)
    words = [w for w in cleaned.strip().lower().split() if w]
    slug = "_".join(words[:max_words])
    return slug or "task"

def build_task_yaml(task_id: str, title: str, domain: str, persona: str, objective: str, depends_on: List[str]) -> str:
    """Builds valid YAML string for an atomic task."""
    if depends_on:
        deps_items = "\n".join([f'  - "{d}"' for d in depends_on])
        deps_block = f"depends_on:\n{deps_items}"
    else:
        deps_block = "depends_on: []"
        
    return (
        f'id: "{task_id}"\n'
        f'title: "{title}"\n'
        f'status: "PENDING"\n'
        f'domain: "{domain}"\n'
        f'assigned_persona: "{persona}"\n'
        f'description: >\n'
        f'  {objective}\n'
        f'{deps_block}\n'
        f'acceptance_criteria:\n'
        f'  - "{objective}"\n'
        f'  - "Zero regressions verified across all verification gates (python3 scripts/verify.py --execute --terse)."\n'
        f'  - "100% test parity with complete boundary test coverage."\n'
    )

def _is_task_already_done(task_file: Path) -> bool:
    if not task_file.exists():
        return False
    try:
        content = task_file.read_text(encoding="utf-8")
        return bool(re.search(r'status:\s*(["\']?)DONE\1', content))
    except Exception as exc:
        sys.stderr.write(f"Read notice for {task_file.name}: {exc}\n")
        return False

def decompose_intent(file_path: str, output_dir: Optional[Path] = None, force: bool = False) -> List[Path]:
    """Decomposes intent objectives into atomic task YAML files."""
    target_dir = output_dir or (ROOT / "tasks")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "r", encoding="utf-8") as f:
        intent = load_yaml(f.read())
        
    if not isinstance(intent, dict):
        raise ValueError("Intent must be a YAML dictionary mapping.")
        
    objectives = intent.get("objectives", [])
    if not objectives or not isinstance(objectives, list):
        print("⚠️ No objectives found in intent. Nothing to decompose.")
        return []

    created_paths: List[Path] = []
    task_ids: List[str] = []

    for idx, obj in enumerate(objectives, 1):
        obj_text = str(obj).strip()
        slug = slugify(obj_text)
        task_id = f"{idx:02d}_{slug}"
        task_file = target_dir / f"{task_id}.yaml"
        task_ids.append(task_id)

        if not force and _is_task_already_done(task_file):
            print(f"⏩ [Decompose] {task_file.name} already marked DONE. Skipping.")
            created_paths.append(task_file)
            continue

        domain, persona = infer_task_domain(obj_text)
        deps = [task_ids[idx - 2]] if idx > 1 else []
        yaml_content = build_task_yaml(task_id, obj_text[:60], domain, persona, obj_text, deps)
        task_file.write_text(yaml_content, encoding="utf-8")
        print(f"✅ [Decompose] Created {task_file.name} -> {persona} (deps: {deps})")
        created_paths.append(task_file)

    return created_paths

def compile_intent(file_path: str) -> bool:
    print(f"[INTENT COMPILER] Validating strict intent specification from {file_path}...")
    if not os.path.exists(file_path):
        print(f"ERROR: Intent Validation Failed. File '{file_path}' does not exist. Vibe coding blocked.")
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            intent = load_yaml(f.read())
            
        if not isinstance(intent, dict):
            raise ValueError("Intent must be a YAML dictionary mapping.")
            
        required_fields = ["name", "status"]
        for field in required_fields:
            if field not in intent:
                raise ValueError(f"Missing required strict field: '{field}'")
                
        status = str(intent.get("status", "")).upper()
        if status not in ("IN_PROGRESS", "DONE"):
            raise ValueError(f"Status must be 'IN_PROGRESS' or 'DONE', got '{status}'")

        # Validate list structures if present
        for list_key in ("objectives", "constraints", "core_philosophy"):
            items = intent.get(list_key)
            if items is not None and not isinstance(items, list):
                raise ValueError(f"Field '{list_key}' must be a list if defined.")

        print(f"[INTENT COMPILER] Validation passed. Intent '{intent['name']}' (status: {status}) conforms to AAC standards.")
        
        out_dir = ROOT / ".agents" / "harness"
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "compiled_intent.json", "w", encoding="utf-8") as out:
            json.dump(intent, out, indent=2)
        return True
            
    except Exception as e:
        err_msg = str(e)
        if "yaml" in type(e).__name__.lower() or "syntax" in err_msg.lower():
            print(f"ERROR: Invalid YAML syntax. Vibe coding blocked.\n{e}")
        else:
            print(f"ERROR: Intent Validation Failed. Vibe coding blocked.\n{e}")
        return False

def main() -> int:
    parser = argparse.ArgumentParser(description="Strict Intent Compiler & Auto-Decomposition Engine")
    parser.add_argument("intent_file", nargs="?", default="intent.yaml", help="Path to intent.yaml (default: intent.yaml)")
    parser.add_argument("--decompose", action="store_true", help="Auto-decompose intent objectives into atomic tasks/*.yaml")
    parser.add_argument("--output-dir", type=str, default=None, help="Target directory for decomposed tasks (default: tasks/)")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing task files")
    args = parser.parse_args()

    success = compile_intent(args.intent_file)
    if not success:
        return 1

    if args.decompose:
        out_dir = Path(args.output_dir) if args.output_dir else None
        decomposed = decompose_intent(args.intent_file, output_dir=out_dir, force=args.force)
        print(f"✨ Successfully decomposed {len(decomposed)} task(s) from intent specification.")

    return 0

if __name__ == '__main__':
    sys.exit(main())
