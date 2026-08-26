import unittest
import os
import tempfile
import sys
import json
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

# Add the root directory to sys.path to import scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.semantic_grapher import (
    CodeGraph,
    parse_python,
    parse_regex,
    scan_directory,
    build_repository_graph
)

class TestSemanticGrapher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_python(self):
        content = """
class MyClass:
    def my_method(self, arg1: int):
        pass

def my_func():
    return True
"""
        filepath = Path(self.temp_dir.name) / "test.py"
        filepath.write_text(content)
        
        graph = CodeGraph()
        f = StringIO()
        with redirect_stdout(f):
            parse_python(filepath, graph)
        
        result = f.getvalue()
        self.assertIn("class MyClass", result)
        self.assertIn("def my_method(self, arg1)", result)
        self.assertIn("def my_func()", result)
        self.assertIn("MyClass", graph.nodes)
        self.assertIn("my_func", graph.nodes)

    def test_parse_regex_ts(self):
        content = """
export class UserService {
  getUser(id: string): User {}
}
const myArrowFunc = (a: number) => { return a; };
function regularFunc() {}
"""
        filepath = Path(self.temp_dir.name) / "test.ts"
        filepath.write_text(content)
        
        graph = CodeGraph()
        f = StringIO()
        with redirect_stdout(f):
            parse_regex(filepath, "ts", graph)
        
        result = f.getvalue()
        self.assertIn("class UserService", result)
        self.assertIn("func/arrow myArrowFunc", result)
        self.assertIn("func/arrow regularFunc", result)
        self.assertIn("UserService", graph.nodes)

    def test_parse_regex_go(self):
        content = """
type User struct {
    ID string
}
func GetUser(id string) User {}
func (u *User) Save() error {}
"""
        filepath = Path(self.temp_dir.name) / "test.go"
        filepath.write_text(content)
        
        graph = CodeGraph()
        f = StringIO()
        with redirect_stdout(f):
            parse_regex(filepath, "go", graph)
        
        result = f.getvalue()
        self.assertIn("struct User", result)
        self.assertIn("func GetUser", result)
        self.assertIn("func Save", result)
        self.assertIn("User", graph.nodes)

    def test_graph_path_and_blast_radius(self):
        graph = CodeGraph()
        graph.add_node("DB", "Database", "module")
        graph.add_node("Repo", "UserRepository", "class")
        graph.add_node("Service", "UserService", "class")
        graph.add_node("Controller", "UserController", "class")

        graph.add_edge("Controller", "Service", "calls")
        graph.add_edge("Service", "Repo", "calls")
        graph.add_edge("Repo", "DB", "queries")

        # Shortest path from Controller to DB
        path = graph.find_shortest_path("Controller", "DB")
        self.assertEqual(path, ["Controller", "Service", "Repo", "DB"])

        # Blast radius of DB (all upstream callers)
        blast = graph.get_blast_radius("DB")
        self.assertIn("Repo", blast)
        self.assertIn("Service", blast)
        self.assertIn("Controller", blast)

        # God nodes
        gods = graph.get_god_nodes()
        self.assertTrue(len(gods) > 0)

if __name__ == '__main__':
    unittest.main()
