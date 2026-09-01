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

        path = graph.find_shortest_path("Controller", "DB")
        self.assertEqual(path, ["Controller", "Service", "Repo", "DB"])

        blast = graph.get_blast_radius("DB")
        self.assertIn("Repo", blast)
        self.assertIn("Service", blast)
        self.assertIn("Controller", blast)

        gods = graph.get_god_nodes()
        self.assertTrue(len(gods) > 0)

        ranks = graph.compute_pagerank()
        self.assertTrue(len(ranks) > 0)
        self.assertIn("DB", ranks)
        self.assertGreater(ranks["DB"], ranks["Controller"])

    def test_main_cli_execution(self):
        from scripts.semantic_grapher import main
        test_py = Path(self.temp_dir.name) / "sample.py"
        test_py.write_text("class TestClass:\n    def sample_func(self):\n        pass\n")

        orig_argv = sys.argv
        try:
            sys.argv = ["semantic_grapher.py", self.temp_dir.name, "--blast-radius", "TestClass"]
            f = StringIO()
            with redirect_stdout(f):
                main()
            self.assertIn("Blast Radius for [TestClass]", f.getvalue())

            sys.argv = ["semantic_grapher.py", self.temp_dir.name, "--json"]
            f = StringIO()
            with redirect_stdout(f):
                main()
            self.assertIn("nodes", f.getvalue())

            sys.argv = ["semantic_grapher.py", self.temp_dir.name, "--pagerank"]
            f = StringIO()
            with redirect_stdout(f):
                main()
            self.assertIn("PageRank Central Symbols", f.getvalue())
        finally:
            sys.argv = orig_argv

if __name__ == '__main__':
    unittest.main()
