#!/usr/bin/env python3
"""
Semantic Grapher (Graphify Engine): Extracts classes, functions, method signatures,
imports, and relationships to build a navigable Knowledge Graph of the repository.
Inspired by Graphify-Labs/graphify.
"""

import ast
import os
import re
import sys
import json
import argparse
from collections import deque
from pathlib import Path

class CodeGraph:
    def __init__(self):
        self.nodes = {}  # id -> dict
        self.edges = []  # list of dicts

    def add_node(self, node_id: str, label: str, node_type: str, file_path: str = "", line: int = 0, signature: str = ""):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "label": label,
                "type": node_type,
                "file": file_path,
                "line": line,
                "signature": signature
            }

    def add_edge(self, source: str, target: str, relation: str, weight: float = 1.0):
        if not source or not target or source == target:
            return
        edge_obj = {
            "source": source,
            "target": target,
            "relation": relation,
            "weight": weight
        }
        self.edges.append(edge_obj)

    def to_dict(self) -> dict:
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }

    def get_forward_adj(self) -> dict:
        adj = {nid: [] for nid in self.nodes}
        for e in self.edges:
            src, tgt = e["source"], e["target"]
            if src in adj:
                adj[src].append(tgt)
        return adj

    def get_reverse_adj(self) -> dict:
        radj = {nid: [] for nid in self.nodes}
        for e in self.edges:
            src, tgt = e["source"], e["target"]
            if tgt in radj:
                radj[tgt].append(src)
        return radj

    def find_shortest_path(self, source_id: str, target_id: str) -> list:
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        if source_id == target_id:
            return [source_id]

        adj = self.get_forward_adj()
        queue = deque([[source_id]])
        visited = {source_id}

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current == target_id:
                return path

            unvisited = [n for n in adj.get(current, []) if n not in visited]
            visited.update(unvisited)
            queue.extend([path + [n] for n in unvisited])
        return []

    def get_blast_radius(self, node_id: str) -> list:
        """Finds all upstream dependents that will break if this node is modified."""
        if node_id not in self.nodes:
            matched = [nid for nid, n in self.nodes.items() if node_id in (n["label"], n["file"], nid)]
            if not matched:
                return []
            node_id = matched[0]

        radj = self.get_reverse_adj()
        queue = deque([node_id])
        visited = set()

        while queue:
            curr = queue.popleft()
            unvisited = [p for p in radj.get(curr, []) if p not in visited]
            visited.update(unvisited)
            queue.extend(unvisited)
        return sorted(list(visited))

    def get_god_nodes(self, top_k: int = 5) -> list:
        """Identifies architectural God Nodes (highest connectivity)."""
        degrees = {nid: 0 for nid in self.nodes}
        for e in self.edges:
            src, tgt = e["source"], e["target"]
            if src in degrees:
                degrees[src] += 1
            if tgt in degrees:
                degrees[tgt] += 1
        sorted_nodes = sorted(degrees.items(), key=lambda item: item[1], reverse=True)
        return sorted_nodes[:top_k]

def print_class_methods(class_node, filepath: Path, graph: CodeGraph):
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            args = [a.arg for a in item.args.args]
            sig = f"def {item.name}({', '.join(args)})"
            print(f"    {sig}")
            method_id = f"{class_node.name}.{item.name}"
            graph.add_node(method_id, method_id, "method", str(filepath), item.lineno, sig)
            graph.add_edge(class_node.name, method_id, "defines")

def parse_python(filepath: Path, graph: CodeGraph | None = None):
    if graph is None:
        graph = CodeGraph()
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        file_id = str(filepath)
        graph.add_node(file_id, filepath.name, "file", file_id)
        
        print(f"\n[FILE] {filepath}")
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                print(f"  class {node.name}:")
                graph.add_node(node.name, node.name, "class", file_id, node.lineno)
                graph.add_edge(file_id, node.name, "defines")
                print_class_methods(node, filepath, graph)
            elif isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                sig = f"def {node.name}({', '.join(args)})"
                print(f"  {sig}")
                graph.add_node(node.name, node.name, "function", file_id, node.lineno, sig)
                graph.add_edge(file_id, node.name, "defines")
            elif isinstance(node, ast.ImportFrom) and node.module:
                graph.add_node(node.module, node.module, "module")
                graph.add_edge(file_id, node.module, "imports")
    except Exception as e:
        print(f"\n[FILE] {filepath} (Error parsing AST: {e})")

def parse_regex(filepath: Path, lang: str, graph: CodeGraph | None = None):
    if graph is None:
        graph = CodeGraph()
    try:
        content = filepath.read_text(encoding="utf-8")
        file_id = str(filepath)
        graph.add_node(file_id, filepath.name, "file", file_id)
        print(f"\n[FILE] {filepath}")
        
        if lang in ["ts", "js"]:
            classes = re.findall(r'class\s+([A-Za-z0-9_]+)', content)
            functions = re.findall(r'(?:function\s+|const\s+|let\s+)([A-Za-z0-9_]+)\s*(?:=|:)?\s*(?:\([^)]*\)\s*=>|\([^)]*\)\s*\{)', content)
            for c in classes:
                print(f"  class {c}")
                graph.add_node(c, c, "class", file_id)
                graph.add_edge(file_id, c, "defines")
            for f in functions:
                print(f"  func/arrow {f}")
                graph.add_node(f, f, "function", file_id)
                graph.add_edge(file_id, f, "defines")
        elif lang == "go":
            structs = re.findall(r'type\s+([A-Za-z0-9_]+)\s+struct', content)
            functions = re.findall(r'func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\(', content)
            for s in structs:
                print(f"  struct {s}")
                graph.add_node(s, s, "struct", file_id)
                graph.add_edge(file_id, s, "defines")
            for f in functions:
                print(f"  func {f}")
                graph.add_node(f, f, "function", file_id)
                graph.add_edge(file_id, f, "defines")
    except Exception as e:
        print(f"\n[FILE] {filepath} (Error parsing: {e})")

def process_files_for_ext(dirpath, filenames, ext, graph: CodeGraph):
    for filename in filenames:
        if filename.endswith(ext):
            filepath = Path(dirpath) / filename
            if ext == ".py":
                parse_python(filepath, graph)
            else:
                parse_regex(filepath, ext[1:], graph)

def process_extension(root_dir: Path, ext: str, graph: CodeGraph):
    excludes = {"node_modules", ".venv", ".git", "graphify-out", "__pycache__"}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        process_files_for_ext(dirpath, filenames, ext, graph)

def build_repository_graph(root_dir: Path) -> CodeGraph:
    graph = CodeGraph()
    for ext in [".py", ".ts", ".js", ".go"]:
        process_extension(root_dir, ext, graph)
    return graph

def scan_directory(root_dir: Path, graph: CodeGraph | None = None):
    if graph is None:
        graph = CodeGraph()
    print(f"Semantic Knowledge Graph for {root_dir}\n" + "="*40)
    for ext in [".py", ".ts", ".js", ".go"]:
        process_extension(root_dir, ext, graph)
    return graph

def main():
    parser = argparse.ArgumentParser(description="Semantic Grapher Knowledge Engine")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output full graph as JSON")
    parser.add_argument("--path-find", nargs=2, metavar=("SRC", "DST"), help="Find shortest path between two symbols")
    parser.add_argument("--blast-radius", metavar="NODE", help="Calculate blast radius for a symbol/file")
    parser.add_argument("--summary", action="store_true", help="Show god nodes and architecture summary")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    graph = CodeGraph()

    if args.json:
        # Build silently
        for ext in [".py", ".ts", ".js", ".go"]:
            process_extension(target, ext, graph)
        print(json.dumps(graph.to_dict(), indent=2))
        return

    if args.path_find:
        for ext in [".py", ".ts", ".js", ".go"]:
            process_extension(target, ext, graph)
        src, dst = args.path_find
        path = graph.find_shortest_path(src, dst)
        if path:
            print(f"Shortest Path ({src} -> {dst}):\n  " + " -> ".join(path))
        else:
            print(f"No direct path found between '{src}' and '{dst}'.")
        return

    if args.blast_radius:
        for ext in [".py", ".ts", ".js", ".go"]:
            process_extension(target, ext, graph)
        dependents = graph.get_blast_radius(args.blast_radius)
        print(f"Blast Radius for [{args.blast_radius}]: ({len(dependents)} impacted dependents)")
        for dep in dependents:
            info = graph.nodes.get(dep, {})
            print(f"  - {dep} ({info.get('type', 'unknown')}) in {info.get('file', '')}")
        return

    # Default scan & summary
    scan_directory(target, graph)
    
    if args.summary or True:
        gods = graph.get_god_nodes(5)
        print("\n" + "="*40 + "\n🏛️ ARCHITECTURAL GOD NODES (Highest Connectivity):")
        for nid, deg in gods:
            n = graph.nodes.get(nid, {})
            print(f"  - [{deg} connections] {nid} ({n.get('type', 'symbol')})")

if __name__ == "__main__":
    main()
