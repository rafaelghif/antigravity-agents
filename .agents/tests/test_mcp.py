import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import importlib.util

# Dynamically load the custom mcp server module
cmd_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/mcp_server.py'))
spec = importlib.util.spec_from_file_location("custom_mcp_server", cmd_file)
mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server)

class TestMcpServer(unittest.TestCase):

    def test_list_tools(self):
        tools_list = mcp_server.list_tools()
        self.assertIn("tools", tools_list)
        names = [t["name"] for t in tools_list["tools"]]
        self.assertIn("log_token_usage", names)
        self.assertIn("get_token_status", names)
        self.assertIn("acquire_module_lock", names)
        self.assertIn("release_module_lock", names)
        self.assertIn("run_validation", names)

    def test_handle_initialize(self):
        msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["protocolVersion"], "2024-11-05")

    def test_handle_list_tools(self):
        msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["id"], 2)
        self.assertIn("tools", res["result"])

    @patch('sys.exit')
    def test_call_tool_unknown(self, mock_exit):
        res = mcp_server.call_tool("invalid_tool_name", {})
        self.assertTrue(res.get("isError"))

if __name__ == '__main__':
    unittest.main()
