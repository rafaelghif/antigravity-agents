#!/usr/bin/env python3
"""
Semantic Grapher - AST-driven code structure mapper and GraphRAG generator.
Supports Python (native ast), TypeScript, and Go via regex.
Features:
- PageRank Centrality: Identifies the most structurally critical hub symbols.
- GraphRAG JSON: Full knowledge graph with typed nodes and edges.
- Blast Radius Analysis: Computes transitive upstream callers impacted by refactoring.
- Shortest-Path Tracer: Computes BFS shortest dependency path between any two symbols.
"""
import ast
import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict, deque

class CodeGraph:
    def __init__(self):
        self.nodes = {}  # symbol_id -> {type, name, file, line}
        self.edges = defaultdict(list)  # symbol_id -> list of (target_symbol_id, relation_type)
        self.reverse_edges = defaultdict(list) # target_symbol_id -> list of (source_symbol_id, relation_type)

    def add_node(self, symbol_id, name, symbol_type, file_path="", line_number=0):
        if symbol_id not in self.nodes:
            self.nodes[symbol_id] = {
                "id": symbol_id,
                "name": name,
                "type": symbol_type,
                "file": str(file_path),
                "line": line_number
            }

    def add_edge(self, source, target, relation):
        self.edges[source].append((target, relation))
        self.reverse_edges[target].append((source, relation))

    def _process_blast_radius_neighbors(self, current, visited, blast_radius, queue):
        for parent, rel in self.reverse_edges.get(current, []):
            if parent not in visited:
                visited.add(parent)
                blast_radius.append({"symbol": parent, "relation": rel, "affected_by": current})
                queue.append(parent)

    def get_blast_radius(self, target_symbol):
        """BFS reverse traversal to find all upstream dependers (blast radius)."""
        visited = set()
        queue = deque([target_symbol])
        blast_radius = []

        while queue:
            current = queue.popleft()
            self._process_blast_radius_neighbors(current, visited, blast_radius, queue)
        return blast_radius

    def _process_shortest_path_neighbors(self, node, end_node, visited, queue, path):
        for neighbor, _ in self.edges.get(node, []):
            if neighbor == end_node:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
        return None

    def find_shortest_path(self, start_node, end_node):
        """BFS shortest path between two symbols."""
        if start_node == end_node:
            return [start_node]
        visited = {start_node}
        queue = deque([[start_node]])

        while queue:
            path = queue.popleft()
            node = path[-1]
            res = self._process_shortest_path_neighbors(node, end_node, visited, queue, path)
            if res:
                return res
        return []

    def get_god_nodes(self, top_n=5):
        """Identifies architectural hub nodes (highest degree centrality)."""
        degrees = {}
        for node in self.nodes:
            in_deg = len(self.reverse_edges.get(node, []))
            out_deg = len(self.edges.get(node, []))
            degrees[node] = in_deg + out_deg
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]

    def _compute_pagerank_step(self, nodes, rank, out_counts, damping, dangling_contrib, n):
        new_rank = {}
        for node in nodes:
            incoming_sum = sum(
                rank[src] / out_counts[src]
                for src, _ in self.reverse_edges.get(node, [])
                if out_counts[src] > 0
            )
            new_rank[node] = (1.0 - damping) / n + damping * incoming_sum + dangling_contrib
        return new_rank

    def compute_pagerank(self, damping=0.85, max_iter=50, tol=1e-6):
        """
        Computes PageRank centrality for nodes in the knowledge graph.
        Higher PageRank = architectural hub node referenced directly/indirectly by many modules.
        """
        nodes = list(self.nodes.keys())
        n = len(nodes)
        if n == 0:
            return {}

        rank = {node: 1.0 / n for node in nodes}
        out_counts = {node: len(self.edges.get(node, [])) for node in nodes}

        for _ in range(max_iter):
            dangling_sum = sum(rank[node] for node in nodes if out_counts[node] == 0)
            dangling_contrib = (damping * dangling_sum) / n

            new_rank = self._compute_pagerank_step(nodes, rank, out_counts, damping, dangling_contrib, n)

            diff = sum(abs(new_rank[node] - rank[node]) for node in nodes)
            rank = new_rank
            if diff < tol:
                break

        total = sum(rank.values())
        if total > 0:
            rank = {k: v / total for k, v in rank.items()}
        return rank

    def export_graphrag_json(self):
        """Exports graph in a standard GraphRAG JSON schema."""
        nodes_list = list(self.nodes.values())
        
        edges_list = [
            {"source": src, "target": dst, "relation": rel}
            for src, targets in self.edges.items()
            for dst, rel in targets
        ]
        
        return json.dumps({"nodes": nodes_list, "edges": edges_list}, indent=2)


def _parse_python_methods(node, class_id, filepath, graph):
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            method_id = f"method:{node.name}.{item.name}"
            args = [a.arg for a in item.args.args]
            graph.add_node(method_id, f"{node.name}.{item.name}", "method", filepath, item.lineno)
            graph.add_edge(class_id, method_id, "contains")
            print(f"  └─ def {item.name}({', '.join(args)}) at line {item.lineno}")

def parse_python(filepath, graph):
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))
        
        file_id = f"file:{filepath.name}"
        graph.add_node(file_id, filepath.name, "file", filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_id = f"class:{node.name}"
                graph.add_node(class_id, node.name, "class", filepath, node.lineno)
                graph.add_edge(file_id, class_id, "defines")
                print(f"[AST] Found class {node.name} at {filepath.name}:{node.lineno}")
                
                _parse_python_methods(node, class_id, filepath, graph)

            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (classes already caught above)
                func_id = f"func:{node.name}"
                args = [a.arg for a in node.args.args]
                graph.add_node(func_id, node.name, "function", filepath, node.lineno)
                graph.add_edge(file_id, func_id, "defines")
                print(f"[AST] Found def {node.name}({', '.join(args)}) at {filepath.name}:{node.lineno}")
    except Exception as e:
        sys.stderr.write(f"Error parsing Python file {filepath}: {e}\n")


def _register_class_nodes(matches, file_id, filepath, graph, lang_label=""):
    for c in matches:
        name = c.group(1)
        cid = f"class:{name}"
        graph.add_node(cid, name, "class", filepath)
        graph.add_edge(file_id, cid, "defines")
        if lang_label:
            print(f"[{lang_label}] Found class {name} in {filepath.name}")

def parse_regex(filepath, lang, graph):
    try:
        content = filepath.read_text(encoding='utf-8')
        file_id = f"file:{filepath.name}"
        graph.add_node(file_id, filepath.name, "file", filepath)

        if lang in ["ts", "js"]:
            classes = re.finditer(r'(?:export\s+)?class\s+([A-Za-z0-9_]+)', content)
            _register_class_nodes(classes, file_id, filepath, graph, lang.upper())

            functions = re.finditer(r'(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', content)
            for f in functions:
                name = f.group(1) or f.group(2)
                if name:
                    fid = f"func:{name}"
                    graph.add_node(fid, name, "function", filepath)
                    graph.add_edge(file_id, fid, "defines")
                    print(f"[{lang.upper()}] Found func/arrow {name} in {filepath.name}")

        elif lang == "go":
            structs = re.finditer(r'type\s+([A-Za-z0-9_]+)\s+struct', content)
            for s in structs:
                name = s.group(1)
                sid = f"struct:{name}"
                graph.add_node(sid, name, "struct", filepath)
                graph.add_edge(file_id, sid, "defines")
                print(f"[GO] Found struct {name} in {filepath.name}")

            funcs = re.finditer(r'func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\(', content)
            for f in funcs:
                name = f.group(1)
                fid = f"func:{name}"
                graph.add_node(fid, name, "function", filepath)
                graph.add_edge(file_id, fid, "defines")
                print(f"[GO] Found func {name} in {filepath.name}")

        elif lang == "rust":
            items = re.finditer(r'(?:pub\s+)?(?:struct|enum)\s+([A-Za-z0-9_]+)', content)
            for it in items:
                name = it.group(1)
                sid = f"type:{name}"
                graph.add_node(sid, name, "type", filepath)
                graph.add_edge(file_id, sid, "defines")
                print(f"[RUST] Found type {name} in {filepath.name}")

            funcs = re.finditer(r'(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z0-9_]+)\s*\(', content)
            for f in funcs:
                name = f.group(1)
                fid = f"func:{name}"
                graph.add_node(fid, name, "function", filepath)
                graph.add_edge(file_id, fid, "defines")
                print(f"[RUST] Found fn {name} in {filepath.name}")

        elif lang in ["java", "csharp", "kotlin"]:
            classes = re.finditer(r'(?:public|private|protected|internal)?\s*(?:class|interface|record)\s+([A-Za-z0-9_]+)', content)
            _register_class_nodes(classes, file_id, filepath, graph, lang.upper())

            methods = re.finditer(r'(?:public|private|protected)?\s+(?:static\s+)?[A-Za-z0-9_<>[\]]+\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*[{;]', content)
            for m in methods:
                name = m.group(1)
                if name not in ("if", "for", "while", "switch", "catch"):
                    fid = f"method:{name}"
                    graph.add_node(fid, name, "method", filepath)
                    graph.add_edge(file_id, fid, "defines")

        elif lang == "php":
            classes = re.finditer(r'class\s+([A-Za-z0-9_]+)', content)
            _register_class_nodes(classes, file_id, filepath, graph)

            funcs = re.finditer(r'function\s+([A-Za-z0-9_]+)\s*\(', content)
            for f in funcs:
                name = f.group(1)
                fid = f"func:{name}"
                graph.add_node(fid, name, "function", filepath)
                graph.add_edge(file_id, fid, "defines")

        elif lang == "ruby":
            classes = re.finditer(r'class\s+([A-Za-z0-9_:]+)', content)
            _register_class_nodes(classes, file_id, filepath, graph)

            funcs = re.finditer(r'def\s+([A-Za-z0-9_!?]+)', content)
            for f in funcs:
                name = f.group(1)
                fid = f"func:{name}"
                graph.add_node(fid, name, "function", filepath)
                graph.add_edge(file_id, fid, "defines")
    except Exception as e:
        sys.stderr.write(f"Error parsing {lang} file {filepath}: {e}\n")


def _scan_files_in_dir(root, files, graph):
    for file in files:
        path = Path(root) / file
        if file.endswith('.py'):
            parse_python(path, graph)
        elif file.endswith(('.ts', '.tsx', '.js', '.jsx')):
            parse_regex(path, "ts", graph)
        elif file.endswith('.go'):
            parse_regex(path, "go", graph)
        elif file.endswith('.rs'):
            parse_regex(path, "rust", graph)
        elif file.endswith(('.java', '.kt')):
            parse_regex(path, "java", graph)
        elif file.endswith('.cs'):
            parse_regex(path, "csharp", graph)
        elif file.endswith('.php'):
            parse_regex(path, "php", graph)
        elif file.endswith('.rb'):
            parse_regex(path, "ruby", graph)

def scan_directory(directory, graph):
    for root, _, files in os.walk(directory):
        if any(ign in root for ign in ['.git', 'node_modules', 'dist', 'build', '.venv', '__pycache__', '.agents-backups']):
            continue
        _scan_files_in_dir(root, files, graph)


def build_repository_graph(target_dir="."):
    graph = CodeGraph()
    scan_directory(target_dir, graph)
    return graph


def main():
    parser = argparse.ArgumentParser(description="AST Code Grapher and Blast Radius Analyzer")
    parser.add_argument("dir", nargs="?", default=".", help="Target directory to map")
    parser.add_argument("--json", action="store_true", help="Output GraphRAG JSON schema")
    parser.add_argument("--blast-radius", type=str, default="", help="Calculate blast radius for a symbol")
    parser.add_argument("--path-find", nargs=2, metavar=("START", "END"), help="Find shortest path between two symbols")
    parser.add_argument("--pagerank", action="store_true", help="Display PageRank centrality ranking")
    parser.add_argument("--top-central", type=int, default=10, help="Number of top PageRank nodes to display")
    
    # Support positional subcommands like 'blast-radius <symbol>' or 'scan'
    if len(sys.argv) > 2 and sys.argv[1] == "blast-radius":
        sys.argv = [sys.argv[0], "--blast-radius", sys.argv[2]]
    elif len(sys.argv) > 1 and sys.argv[1] == "scan":
        sys.argv = [sys.argv[0], "."]
        
    args = parser.parse_args()

    graph = build_repository_graph(args.dir)

    if args.json:
        print(graph.export_graphrag_json())
        return

    if args.blast_radius:
        blast = graph.get_blast_radius(args.blast_radius)
        print(f"\n--- Blast Radius for [{args.blast_radius}] ---")
        if not blast:
            print("No upstream dependers found or isolated symbol.")
        for item in blast:
            print(f"  <- Affected: {item['symbol']} (via {item['relation']} to {item['affected_by']})")
        return

    if args.path_find:
        start, end = args.path_find
        path = graph.find_shortest_path(start, end)
        print(f"\n--- Shortest Path: {start} -> {end} ---")
        if path:
            print(" -> ".join(path))
        else:
            print("No connection path found.")
        return

    if args.pagerank:
        ranks = graph.compute_pagerank()
        sorted_ranks = sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:args.top_central]
        print(f"\n--- Top {len(sorted_ranks)} PageRank Central Symbols ---")
        for sym, rank_val in sorted_ranks:
            node_info = graph.nodes.get(sym, {})
            fpath = node_info.get("file", "")
            stype = node_info.get("type", "")
            print(f"  [{stype.upper():<8}] {sym:<30} (Rank: {rank_val:.4f}) -> {fpath}")
        return

    gods = graph.get_god_nodes()
    print("\n--- Architectural Hub Nodes (Degree Centrality) ---")
    for node, deg in gods:
        print(f"  Hub Symbol: {node:<30} (Degree: {deg})")


if __name__ == '__main__':
    main()
