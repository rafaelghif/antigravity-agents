import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import importlib.util
from datetime import datetime, timedelta

# Dynamically load the custom token command module to avoid built-in token module namespace conflict
cmd_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands/token.py'))
spec = importlib.util.spec_from_file_location("custom_token_cmd", cmd_file)
token_cmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(token_cmd)

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestTokenCommand(unittest.TestCase):

    @patch('os.path.exists', return_value=False)
    def test_load_budget_default(self, mock_exists):
        budget = token_cmd.load_budget()
        self.assertEqual(budget["daily_used"], 0)
        self.assertEqual(budget["monthly_used"], 0)
        self.assertEqual(budget["monthly_limit"], 5000000)
        self.assertEqual(budget["daily_limit"], 500000)
        self.assertEqual(budget["tasks"], {})
        self.assertEqual(budget["accounts"], {})

    @patch('sys.exit', side_effect=raise_system_exit)
    def test_log_success(self, mock_exit):
        # Use patch.object to mock methods on the dynamically loaded module
        with patch.object(token_cmd, 'load_budget') as mock_load, \
             patch.object(token_cmd, 'save_budget') as mock_save, \
             patch.object(token_cmd, 'append_to_log') as mock_append, \
             patch.object(token_cmd, 'get_active_api_account', return_value="gemini:AIza...1234"):
             
            mock_load.return_value = {
                "monthly_limit": 5000000,
                "monthly_used": 0,
                "daily_limit": 500000,
                "daily_used": 0,
                "last_reset": datetime.utcnow().isoformat() + "Z",
                "accounts": {},
                "tasks": {}
            }
            
            # Log 5000 prompt and 1000 completion for task issue-164
            token_cmd.run_log(["5000", "1000", "--task", "issue-164"])
            
            # Verify save_budget is called with updated totals
            mock_save.assert_called_once()
            saved_data = mock_save.call_args[0][0]
            self.assertEqual(saved_data["daily_used"], 6000)
            self.assertEqual(saved_data["monthly_used"], 6000)
            self.assertIn("issue-164", saved_data["tasks"])
            self.assertEqual(saved_data["tasks"]["issue-164"]["total_tokens"], 6000)
            
            # Verify account tracking
            self.assertIn("gemini:AIza...1234", saved_data["accounts"])
            self.assertEqual(saved_data["accounts"]["gemini:AIza...1234"]["total_used"], 6000)

    @patch('sys.exit', side_effect=raise_system_exit)
    def test_log_invalid_values(self, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            token_cmd.run_log(["invalid", "1000"])
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            token_cmd.run_log(["-100", "1000"])
        self.assertEqual(cm.exception.code, 1)

    def test_get_active_api_account_env(self):
        with patch.dict(os.environ, {"ACTIVE_API_PROFILE": "personal-profile"}):
            self.assertEqual(token_cmd.get_active_api_account(), "personal-profile")
            
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyDummyTestKeyForVerification"}):
            # Should mask the key: 'gemini:AIza...tion'
            self.assertEqual(token_cmd.get_active_api_account(), "gemini:AIza...tion")

    def test_check_date_resets_daily(self):
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        budget = {
            "monthly_limit": 5000000,
            "monthly_used": 20000,
            "daily_limit": 500000,
            "daily_used": 10000,
            "last_reset": yesterday,
            "accounts": {
                "gemini:AIza...1234": {
                    "daily_used": 10000,
                    "monthly_used": 20000,
                    "total_used": 30000
                }
            },
            "tasks": {}
        }
        
        updated = token_cmd.check_date_resets(budget)
        self.assertEqual(updated["daily_used"], 0)
        self.assertEqual(updated["monthly_used"], 20000) # Monthly should not be reset on daily boundary
        self.assertEqual(updated["accounts"]["gemini:AIza...1234"]["daily_used"], 0)
        self.assertEqual(updated["accounts"]["gemini:AIza...1234"]["monthly_used"], 20000)

    def test_check_date_resets_monthly(self):
        last_month = (datetime.utcnow() - timedelta(days=32)).isoformat() + "Z"
        budget = {
            "monthly_limit": 5000000,
            "monthly_used": 20000,
            "daily_limit": 500000,
            "daily_used": 10000,
            "last_reset": last_month,
            "accounts": {
                "gemini:AIza...1234": {
                    "daily_used": 10000,
                    "monthly_used": 20000,
                    "total_used": 30000
                }
            },
            "tasks": {}
        }
        
        updated = token_cmd.check_date_resets(budget)
        self.assertEqual(updated["daily_used"], 0)
        self.assertEqual(updated["monthly_used"], 0) # Both should reset
        self.assertEqual(updated["accounts"]["gemini:AIza...1234"]["daily_used"], 0)
        self.assertEqual(updated["accounts"]["gemini:AIza...1234"]["monthly_used"], 0)

    def test_reset_command(self):
        with patch.object(token_cmd, 'load_budget') as mock_load, \
             patch.object(token_cmd, 'save_budget') as mock_save:
             
            mock_load.return_value = {
                "monthly_limit": 5000000,
                "monthly_used": 20000,
                "daily_limit": 500000,
                "daily_used": 10000,
                "last_reset": "2026-06-27T00:00:00Z",
                "accounts": {
                    "gemini:AIza...1234": {
                        "daily_used": 10000,
                        "monthly_used": 20000,
                        "total_used": 30000
                    }
                },
                "tasks": {"issue-164": {}}
            }
            
            token_cmd.run_reset(["--daily"])
            saved_data = mock_save.call_args[0][0]
            self.assertEqual(saved_data["daily_used"], 0)
            self.assertEqual(saved_data["monthly_used"], 20000)
            self.assertEqual(saved_data["accounts"]["gemini:AIza...1234"]["daily_used"], 0)

if __name__ == '__main__':
    unittest.main()
