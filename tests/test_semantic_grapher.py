import unittest
import os
import tempfile
import sys
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

# Add the root directory to sys.path to import scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.semantic_grapher import parse_python, parse_regex, scan_directory

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
        
        f = StringIO()
        with redirect_stdout(f):
            parse_python(filepath)
        
        result = f.getvalue()
        self.assertIn("class MyClass:", result)
        self.assertIn("def my_method(self, arg1)", result)
        self.assertIn("def my_func()", result)

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
        
        f = StringIO()
        with redirect_stdout(f):
            parse_regex(filepath, "ts")
        
        result = f.getvalue()
        self.assertIn("class UserService", result)
        self.assertIn("func/arrow myArrowFunc", result)
        self.assertIn("func/arrow regularFunc", result)

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
        
        f = StringIO()
        with redirect_stdout(f):
            parse_regex(filepath, "go")
        
        result = f.getvalue()
        self.assertIn("struct User", result)
        self.assertIn("func GetUser", result)
        self.assertIn("func Save", result)

if __name__ == '__main__':
    unittest.main()
