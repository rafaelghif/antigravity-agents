import unittest
import os
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.ui_hygiene_guard import audit_ui_content, is_ui_file

class TestUIHygieneGuard(unittest.TestCase):
    def test_is_ui_file(self):
        self.assertTrue(is_ui_file(Path("src/components/Button.tsx")))
        self.assertTrue(is_ui_file(Path("src/pages/index.jsx")))
        self.assertTrue(is_ui_file(Path("src/views/App.vue")))
        self.assertTrue(is_ui_file(Path("src/routes/About.svelte")))
        self.assertTrue(is_ui_file(Path("public/index.html")))

        self.assertFalse(is_ui_file(Path("scripts/verify.py")))
        self.assertFalse(is_ui_file(Path("README.md")))
        self.assertFalse(is_ui_file(Path("package.json")))

    def test_detects_img_without_alt(self):
        bad_jsx = '<img src="/logo.png" className="w-10 h-10" />'
        issues = audit_ui_content(bad_jsx, "Logo.tsx")
        self.assertTrue(any("alt" in issue.lower() for issue in issues))

        good_jsx = '<img src="/logo.png" alt="Company Logo" className="w-10 h-10" />'
        issues = audit_ui_content(good_jsx, "Logo.tsx")
        self.assertFalse(any("alt" in issue.lower() for issue in issues))

    def test_detects_outline_none_without_focus_visible(self):
        bad_jsx = '<button type="button" className="p-2 outline-none">Click</button>'
        issues = audit_ui_content(bad_jsx, "Button.tsx")
        self.assertTrue(any("focus-visible" in issue.lower() for issue in issues))

        good_jsx = '<button type="button" className="p-2 outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Click</button>'
        issues = audit_ui_content(good_jsx, "Button.tsx")
        self.assertFalse(any("focus-visible" in issue.lower() for issue in issues))

    def test_detects_button_missing_type(self):
        bad_jsx = '<button className="btn">Submit</button>'
        issues = audit_ui_content(bad_jsx, "Form.tsx")
        self.assertTrue(any("type" in issue.lower() for issue in issues))

        good_jsx = '<button type="button" className="btn">Submit</button>'
        issues = audit_ui_content(good_jsx, "Form.tsx")
        self.assertFalse(any("type" in issue.lower() for issue in issues))

    def test_detects_inline_hardcoded_hex_colors(self):
        bad_jsx = '<div style={{ backgroundColor: "#1e293b" }}>Card</div>'
        issues = audit_ui_content(bad_jsx, "Card.tsx")
        self.assertTrue(any("hardcoded" in issue.lower() or "hex" in issue.lower() for issue in issues))

        good_jsx = '<div className="bg-slate-800">Card</div>'
        issues = audit_ui_content(good_jsx, "Card.tsx")
        self.assertFalse(any("hardcoded" in issue.lower() or "hex" in issue.lower() for issue in issues))

if __name__ == '__main__':
    unittest.main()
