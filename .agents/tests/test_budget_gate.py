import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import helper

class TestBudgetGate(unittest.TestCase):
    
    @patch('sys.exit')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    def test_gate_allows_token_commands(self, mock_file, mock_exists, mock_exit):
        # Even if budget is exceeded, token status/reset should be allowed
        mock_json_content = json.dumps({
            "daily_limit": 100,
            "daily_used": 200,
            "monthly_limit": 1000,
            "monthly_used": 2000
        })
        mock_file.return_value.__enter__.return_value.read.return_value = mock_json_content
        
        # Test command "token"
        helper.check_token_budget_gate("token")
        mock_exit.assert_not_called()
        
        # Test command "doctor"
        helper.check_token_budget_gate("doctor")
        mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    def test_gate_blocks_on_daily_exceeded(self, mock_file, mock_exists, mock_exit):
        mock_json_content = json.dumps({
            "daily_limit": 100,
            "daily_used": 150,
            "monthly_limit": 1000,
            "monthly_used": 500
        })
        mock_file.return_value.__enter__.return_value.read.return_value = mock_json_content
        
        # Test command "sync"
        helper.check_token_budget_gate("sync")
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    def test_gate_blocks_on_monthly_exceeded(self, mock_file, mock_exists, mock_exit):
        mock_json_content = json.dumps({
            "daily_limit": 1000,
            "daily_used": 500,
            "monthly_limit": 1000,
            "monthly_used": 1200
        })
        mock_file.return_value.__enter__.return_value.read.return_value = mock_json_content
        
        # Test command "sync"
        helper.check_token_budget_gate("sync")
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    def test_gate_allows_within_budget(self, mock_file, mock_exists, mock_exit):
        mock_json_content = json.dumps({
            "daily_limit": 1000,
            "daily_used": 500,
            "monthly_limit": 10000,
            "monthly_used": 5000
        })
        mock_file.return_value.__enter__.return_value.read.return_value = mock_json_content
        
        # Test command "sync"
        helper.check_token_budget_gate("sync")
        mock_exit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
