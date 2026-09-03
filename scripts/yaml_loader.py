#!/usr/bin/env python3
"""
Pure Python stdlib YAML parser fallback for AAC.
Uses PyYAML if available; falls back to an internal pure-stdlib parser
for standard AAC configurations (workflows, intents, tasks, manifests).
Zero external dependencies.
"""
from __future__ import annotations
import re
from typing import Any

def _parse_scalar(v: str) -> Any:
    v = v.strip()
    if v.startswith('[') and v.endswith(']'):
        return [i.strip().strip('"\'') for i in v[1:-1].split(',') if i.strip()]
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    low = v.lower()
    if low == 'true':
        return True
    if low == 'false':
        return False
    if low in ('null', '~', ''):
        return None
    try:
        if '.' in v:
            return float(v)
        return int(v)
    except ValueError:
        return v

def _unwind_stack(stack: list[tuple[int, Any, Any, Any]], indent: int) -> None:
    while len(stack) > 1 and stack[-1][0] > indent:
        stack.pop()

def _fallback_yaml_load(text: str) -> Any:
    lines = text.splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any, Any, Any]] = [(0, root, None, None)]

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())

        _unwind_stack(stack, indent)

        cur_indent, cur_container, parent, pkey = stack[-1]

        if stripped.startswith('- '):
            val = _parse_scalar(stripped[2:])
            if isinstance(cur_container, dict) and not cur_container and parent is not None and pkey is not None:
                new_list = [val]
                parent[pkey] = new_list
                stack[-1] = (cur_indent, new_list, parent, pkey)
            elif isinstance(cur_container, list):
                cur_container.append(val)
            continue

        if ':' in stripped:
            key, _, val = stripped.partition(':')
            key = key.strip().strip('"\'')
            val = val.strip()

            if not val:
                new_dict: dict[str, Any] = {}
                if isinstance(cur_container, dict):
                    cur_container[key] = new_dict
                    stack.append((indent + 2, new_dict, cur_container, key))
            elif val == '[]':
                if isinstance(cur_container, dict):
                    cur_container[key] = []
            elif val.startswith('[') and val.endswith(']'):
                if isinstance(cur_container, dict):
                    cur_container[key] = _parse_scalar(val)
            else:
                if isinstance(cur_container, dict):
                    cur_container[key] = _parse_scalar(val)

    return root

def load_yaml(source: str) -> Any:
    try:
        import yaml
        return yaml.safe_load(source)
    except ImportError:
        return _fallback_yaml_load(source)
