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
             patch.object(token_cmd, 'sync_from_platform_usage', return_value={}) as mock_sync, \
             patch.object(token_cmd, 'get_active_api_account', return_value="gemini:sha256-ba88894d"):
             
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
            self.assertIn("gemini:sha256-ba88894d", saved_data["accounts"])
            self.assertEqual(saved_data["accounts"]["gemini:sha256-ba88894d"]["total_used"], 6000)

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
            # Should mask the key with SHA-256 hash prefix
            self.assertTrue(token_cmd.get_active_api_account().startswith("gemini:sha256-"))
            self.assertEqual(len(token_cmd.get_active_api_account()), len("gemini:sha256-") + 8)

    def test_check_date_resets_daily(self):
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        budget = {
            "monthly_limit": 5000000,
            "monthly_used": 20000,
            "daily_limit": 500000,
            "daily_used": 10000,
            "last_reset": yesterday,
            "accounts": {
                "gemini:sha256-ba88894d": {
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
        self.assertEqual(updated["accounts"]["gemini:sha256-ba88894d"]["daily_used"], 0)
        self.assertEqual(updated["accounts"]["gemini:sha256-ba88894d"]["monthly_used"], 20000)

    def test_check_date_resets_monthly(self):
        last_month = (datetime.utcnow() - timedelta(days=32)).isoformat() + "Z"
        budget = {
            "monthly_limit": 5000000,
            "monthly_used": 20000,
            "daily_limit": 500000,
            "daily_used": 10000,
            "last_reset": last_month,
            "accounts": {
                "gemini:sha256-ba88894d": {
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
        self.assertEqual(updated["accounts"]["gemini:sha256-ba88894d"]["daily_used"], 0)
        self.assertEqual(updated["accounts"]["gemini:sha256-ba88894d"]["monthly_used"], 0)

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
                    "gemini:sha256-ba88894d": {
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
            self.assertEqual(saved_data["accounts"]["gemini:sha256-ba88894d"]["daily_used"], 0)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="I0704 08:38:25.047474 180703 server_oauth.go:219] OAuth: authenticated successfully as test-user@example.com\n")
    @patch('os.path.getmtime', return_value=123456789.0)
    def test_get_active_api_account_logs(self, mock_getmtime, mock_file, mock_listdir, mock_exists):
        def exists_side_effect(path):
            if "active_api_profile_name" in path:
                return False
            return True
        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ["cli-20260704_083824.log"]
        
        with patch.dict(os.environ, {}, clear=True):
            account = token_cmd.get_active_api_account()
            self.assertEqual(account, "test-user@example.com")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_auto_detect_tokens(self, mock_file, mock_exists):
        transcript_data = (
            '{"source": "USER", "content": "hello agent"}\n'
            '{"source": "MODEL", "content": "hello user", "tool_calls": []}\n'
        )
        mock_file.return_value.readlines.return_value = transcript_data.strip().split('\n')
        
        with patch.dict(os.environ, {"ANTIGRAVITY_CONVERSATION_ID": "dummy-conv-id"}):
            prompt, completion = token_cmd.auto_detect_tokens()
            self.assertGreater(prompt, 0)
            self.assertGreater(completion, 0)

    @patch('subprocess.run')
    @patch.object(token_cmd, 'load_budget')
    @patch.object(token_cmd, 'get_current_task_id', return_value="issue-176")
    def test_auto_detect_tokens_via_usage(self, mock_task, mock_load, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = (
            "Task Breakdown:\n"
            "  - issue-176      : 20,000 total (18,000 prompt / 2,000 completion)\n"
        )
        mock_run.return_value = mock_proc

        mock_load.return_value = {
            "tasks": {
                "issue-176": {
                    "prompt_tokens": 15000,
                    "completion_tokens": 114,
                    "total_tokens": 15114
                }
            }
        }

        with patch.dict(os.environ, {"FORCE_PLATFORM_DETECT": "true"}):
            prompt, completion = token_cmd.auto_detect_tokens()
            self.assertEqual(prompt, 3000)
            self.assertEqual(completion, 1886)

    def test_get_reset_intervals_remaining(self):
        resets = token_cmd.get_reset_intervals_remaining()
        self.assertIn("five_hour", resets)
        self.assertIn("daily", resets)
        self.assertIn("weekly", resets)
        self.assertIn("monthly", resets)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"active": "active-json-user@example.com"}')
    def test_get_active_api_account_google_accounts_json(self, mock_file, mock_exists):
        def exists_side_effect(path):
            if "google_accounts.json" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        
        with patch.dict(os.environ, {}, clear=True):
            account = token_cmd.get_active_api_account()
            self.assertEqual(account, "active-json-user@example.com")

    def test_parse_usage_output(self):
        # Table format
        output1 = (
            "### **Token Budget Summary**\n"
            "| Metric | Limit | Used | Utilization |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Daily** | 500,000 tokens | 161,515 tokens | 32.30% |\n"
            "| **Monthly** | 5,000,000 tokens | 161,515 tokens | 3.23% |\n\n"
            "### **Rolling Quotas & Resets**\n"
            "* **5-Hour Rolling Limit:** 200,000 tokens (Used: **179,515 tokens** or **89.76%** utilized)\n"
            "  * *Reset in:* **4 hours, 9 minutes**\n"
            "* **Weekly Rolling Limit:** 2,500,000 tokens (Used: **179,515 tokens** or **7.18%** utilized)\n"
            "  * *Reset in:* **6 days, 23 hours, 9 minutes**\n"
        )
        parsed1 = token_cmd.parse_usage_output(output1)
        self.assertEqual(parsed1["daily_limit"], 500000)
        self.assertEqual(parsed1["daily_used"], 161515)
        self.assertEqual(parsed1["monthly_limit"], 5000000)
        self.assertEqual(parsed1["monthly_used"], 161515)
        self.assertEqual(parsed1["five_hour_limit"], 200000)
        self.assertEqual(parsed1["five_hour_used"], 179515)
        self.assertEqual(parsed1["five_hour_remaining"], "4h 9m")
        self.assertEqual(parsed1["weekly_limit"], 2500000)
        self.assertEqual(parsed1["weekly_used"], 179515)
        self.assertEqual(parsed1["weekly_remaining"], "6d 23h 9m")

        # List format
        output2 = (
            "### Antigravity Token Budget Status\n\n"
            "#### Core Quotas\n"
            "*   **Daily Quota:** `161,515` / `500,000` tokens (**32.30%** utilized)\n"
            "*   **Monthly Quota:** `161,515` / `5,000,000` tokens (**3.23%** utilized)\n\n"
            "#### Rolling Quotas\n"
            "*   **5-Hour Rolling Limit:** `142,000` / `200,000` tokens (**71.00%** utilized) — *Resets in 4h 45m*\n"
            "*   **Weekly Rolling Limit:** `1,950,000` / `2,500,000` tokens (**78.00%** utilized) — *Resets in 131h 47m*\n"
        )
        parsed2 = token_cmd.parse_usage_output(output2)
        self.assertEqual(parsed2["daily_limit"], 500000)
        self.assertEqual(parsed2["daily_used"], 161515)
        self.assertEqual(parsed2["five_hour_used"], 142000)
        self.assertEqual(parsed2["five_hour_limit"], 200000)
        self.assertEqual(parsed2["five_hour_remaining"], "4h 45m")
        self.assertEqual(parsed2["weekly_remaining"], "131h 47m")

        # Console text format
        output3 = (
            "Daily Limit   : 500,000 tokens\n"
            "Daily Used    : 161,515 tokens (32.30% utilized)\n"
            "Monthly Limit : 5,000,000 tokens\n"
            "Monthly Used  : 161,515 tokens (3.23% utilized)\n"
            "  - 5-Hour Rolling Limit : 200,000 tokens\n"
            "  - 5-Hour Rolling Used  : 142,000 tokens (71.00% utilized)\n"
            "  - 5-Hour Reset In      : 4h 45m\n"
            "  - Weekly Rolling Limit : 2,500,000 tokens\n"
            "  - Weekly Rolling Used  : 1,950,000 tokens (78.00% utilized)\n"
            "  - Weekly Reset In      : 131h 47m\n"
        )
        parsed3 = token_cmd.parse_usage_output(output3)
        self.assertEqual(parsed3["daily_limit"], 500000)
        self.assertEqual(parsed3["daily_used"], 161515)
        self.assertEqual(parsed3["five_hour_limit"], 200000)
        self.assertEqual(parsed3["five_hour_used"], 142000)
        self.assertEqual(parsed3["five_hour_remaining"], "4h 45m")
        self.assertEqual(parsed3["weekly_remaining"], "131h 47m")

        # Breakdown parsing format
        output4 = (
            "Daily Limit   : 500,000 tokens\n"
            "Daily Used    : 161,515 tokens\n"
            "Monthly Limit : 5,000,000 tokens\n"
            "Monthly Used  : 161,515 tokens\n"
            "------------------------------------------------------------\n"
            "Account Breakdown:\n"
            "  - merioptasari@gmail.com: daily 15,115 | monthly 15,115 | total 15,115\n"
            "  - default        : daily 92,400 | monthly 92,400 | total 92,400\n"
            "------------------------------------------------------------\n"
            "Task Breakdown:\n"
            "  - issue-176      : 15,114 total (15,000 prompt / 114 completion)\n"
            "  - unknown        : 107,515 total (99,000 prompt / 8,515 completion)\n"
            "============================================================\n"
        )
        parsed4 = token_cmd.parse_usage_output(output4)
        self.assertIn("accounts", parsed4)
        self.assertIn("merioptasari@gmail.com", parsed4["accounts"])
        self.assertEqual(parsed4["accounts"]["merioptasari@gmail.com"]["daily_used"], 15115)
        self.assertEqual(parsed4["accounts"]["default"]["total_used"], 92400)
        self.assertIn("tasks", parsed4)
        self.assertIn("issue-176", parsed4["tasks"])
        self.assertEqual(parsed4["tasks"]["issue-176"]["prompt_tokens"], 15000)
        self.assertEqual(parsed4["tasks"]["issue-176"]["completion_tokens"], 114)
        self.assertEqual(parsed4["tasks"]["issue-176"]["total_tokens"], 15114)

        # Block percentage format
        output5 = (
            "└ Models & Quota\n"
            "\n"
            "  Account: merioptasari@gmail.com\n"
            "\n"
            "GEMINI MODELS\n"
            "  Models within this group: Gemini Flash, Gemini Pro\n"
            "\n"
            "  Weekly Limit\n"
            "    [████████████████████████████████░░░░░░░░░░░░░░░░░░] 63.38%\n"
            "    63% remaining · Refreshes in 125h 11m\n"
            "\n"
            "  Five Hour Limit\n"
            "    [████████████████████████████████████████░░░░░░░░░░] 79.81%\n"
            "    80% remaining · Refreshes in 4h 44m\n"
        )
        parsed5 = token_cmd.parse_usage_output(output5, budget={"weekly_limit": 2500000, "five_hour_limit": 200000})
        self.assertEqual(parsed5["active_account"], "merioptasari@gmail.com")
        self.assertAlmostEqual(parsed5["weekly_pct"], 36.62, places=2)
        self.assertAlmostEqual(parsed5["five_hour_pct"], 20.19, places=2)
        self.assertEqual(parsed5["weekly_remaining"], "125h 11m")
        self.assertEqual(parsed5["five_hour_remaining"], "4h 44m")
        self.assertEqual(parsed5["weekly_limit"], 2500000)
        self.assertEqual(parsed5["five_hour_limit"], 200000)
        self.assertIn("merioptasari@gmail.com", parsed5["accounts"])



    @patch('subprocess.run')
    @patch.object(token_cmd, 'load_budget')
    @patch.object(token_cmd, 'save_budget')
    @patch.object(token_cmd, 'get_rolling_window_stats')
    @patch.object(token_cmd, 'scan_conversations_for_usage', return_value=None)
    def test_sync_from_platform_usage(self, mock_scan, mock_rolling, mock_save, mock_load, mock_run):
        mock_load.return_value = {
            "daily_limit": 500000,
            "daily_used": 0,
            "monthly_limit": 5000000,
            "monthly_used": 0,
            "weekly_limit": 2500000,
            "five_hour_limit": 200000
        }
        mock_rolling.return_value = {
            "weekly_used": 180000,
            "five_hour_used": 20000
        }
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = (
            "└ Models & Quota\n"
            "  Account: merioptasari@gmail.com\n"
            "GEMINI MODELS\n"
            "  Weekly Limit\n"
            "    [████░░░] 63.38%\n"
            "  Five Hour Limit\n"
            "    [████░░░] 79.81%\n"
        )
        mock_run.return_value = mock_proc
        
        parsed = token_cmd.sync_from_platform_usage()
        mock_save.assert_called_once()
        saved_budget = mock_save.call_args[0][0]
        self.assertEqual(saved_budget["weekly_limit"], 491534)
        self.assertEqual(saved_budget["five_hour_limit"], 99058)

    @patch('subprocess.run')
    @patch.object(token_cmd, 'load_budget')
    @patch.object(token_cmd, 'save_budget')
    @patch.object(token_cmd, 'get_rolling_window_stats')
    @patch.object(token_cmd, 'scan_conversations_for_usage')
    def test_sync_from_platform_usage_db(self, mock_scan, mock_rolling, mock_save, mock_load, mock_run):
        mock_load.return_value = {
            "daily_limit": 500000,
            "daily_used": 0,
            "monthly_limit": 5000000,
            "monthly_used": 0,
            "weekly_limit": 2500000,
            "five_hour_limit": 200000
        }
        mock_rolling.return_value = {
            "weekly_used": 180000,
            "five_hour_used": 20000
        }
        usage_text = (
            "└ Models & Quota\n"
            "  Account: merioptasari@gmail.com\n"
            "GEMINI MODELS\n"
            "  Weekly Limit\n"
            "    [████░░░] 63.38%\n"
            "  Five Hour Limit\n"
            "    [████░░░] 79.81%\n"
        )
        mock_scan.return_value = usage_text
        
        parsed = token_cmd.sync_from_platform_usage()
        # Verify subprocess was NOT run since DB search was successful
        mock_run.assert_not_called()
        mock_save.assert_called_once()
        saved_budget = mock_save.call_args[0][0]
        self.assertEqual(saved_budget["weekly_limit"], 491534)
        self.assertEqual(saved_budget["five_hour_limit"], 99058)
        self.assertTrue(parsed.get("synced_from_db"))

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.getmtime')
    @patch('sqlite3.connect')
    def test_scan_conversations_for_usage(self, mock_connect, mock_getmtime, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["conv1.db", "conv2.db"]
        mock_getmtime.side_effect = lambda path: 1000 if "conv1.db" in path else 2000
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = ("steps",)
        
        usage_text = (
            "└ Models & Quota\n"
            "  Account: test@gmail.com\n"
            "GEMINI MODELS\n"
            "  Weekly Limit\n"
            "    [██░░] 50.00%\n"
        )
        mock_cursor.fetchall.return_value = [(usage_text.encode('utf-8'),)]
        
        result = token_cmd.scan_conversations_for_usage()
        self.assertEqual(result, usage_text)
        mock_connect.assert_called_with(os.path.expanduser("~/.gemini/antigravity-cli/conversations/conv2.db"))

if __name__ == '__main__':
    unittest.main()
