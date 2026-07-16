import unittest
import json
import sys
import io
import os
from unittest.mock import patch, MagicMock

# Inject scripts folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import mcp_server

class TestMcpServer(unittest.TestCase):
    def setUp(self):
        mcp_server.is_valid_workspace = True
        self.mock_token = MagicMock()
        self.mock_lock = MagicMock()
        self.mock_validate = MagicMock()
        
        mcp_server.token_cmd = self.mock_token
        mcp_server.lock_cmd = self.mock_lock
        mcp_server.validate_module = self.mock_validate

    def tearDown(self):
        mcp_server.token_cmd = None
        mcp_server.lock_cmd = None
        mcp_server.validate_module = None

    def test_handle_message_invalid_jsonrpc(self):
        # Missing jsonrpc field
        msg = {"method": "initialize", "id": 1}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["error"]["code"], -32600)
        self.assertIn("jsonrpc", res["error"]["message"])

    def test_handle_message_invalid_type(self):
        res = mcp_server.handle_message("not a dict")
        self.assertEqual(res["error"]["code"], -32600)

    def test_handle_message_missing_method(self):
        msg = {"jsonrpc": "2.0", "id": 1}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["error"]["code"], -32600)

    def test_handle_message_method_not_found(self):
        msg = {"jsonrpc": "2.0", "method": "invalid_method", "id": 1}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["error"]["code"], -32601)

    def test_handle_message_initialize(self):
        msg = {"jsonrpc": "2.0", "method": "initialize", "id": 1}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["id"], 1)
        self.assertIn("protocolVersion", res["result"])

    def test_handle_message_tools_list(self):
        msg = {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["id"], 2)
        self.assertIn("tools", res["result"])

    def test_handle_message_tools_call_missing_name(self):
        msg = {"jsonrpc": "2.0", "method": "tools/call", "params": {}, "id": 3}
        res = mcp_server.handle_message(msg)
        self.assertEqual(res["error"]["code"], -32602)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_call_tool_stdout_stderr_redirection(self, mock_stderr, mock_stdout):
        # Setup mock behavior that writes to stdout and stderr
        def mock_run_log(args):
            sys.stdout.write("standard output message")
            sys.stderr.write("standard error warning")
        
        self.mock_token.run_log = mock_run_log
        
        res = mcp_server.call_tool("log_token_usage", {"prompt_tokens": 100, "completion_tokens": 50})
        self.assertFalse(res.get("isError", False))
        text_content = res["content"][0]["text"]
        self.assertIn("standard output message", text_content)
        self.assertIn("standard error warning", text_content)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_call_tool_exception_handling(self, mock_stderr, mock_stdout):
        def mock_run_fail(args):
            raise ValueError("Something went wrong internally")
            
        self.mock_token.run_log = mock_run_fail
        
        res = mcp_server.call_tool("log_token_usage", {"prompt_tokens": 100, "completion_tokens": 50})
        self.assertTrue(res.get("isError"))
        text_content = res["content"][0]["text"]
        self.assertIn("ValueError", text_content)
        self.assertIn("Something went wrong internally", text_content)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_call_tool_system_exit(self, mock_stderr, mock_stdout):
        def mock_run_exit(args):
            sys.stdout.write("finished status")
            sys.exit(0)
            
        self.mock_token.run_log = mock_run_exit
        
        res = mcp_server.call_tool("log_token_usage", {"prompt_tokens": 100, "completion_tokens": 50})
        self.assertFalse(res.get("isError", False))
        self.assertEqual(res["content"][0]["text"], "finished status")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stdin')
    def test_start_server_parse_error(self, mock_stdin, mock_stdout):
        mock_stdin.readline.side_effect = ["malformed json string\n", ""]
        
        mcp_server.start_server()
        
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)
        res = json.loads(output.strip())
        self.assertEqual(res["error"]["code"], -32700)
        self.assertIn("Parse error", res["error"]["message"])

    def test_handle_message_notification(self):
        # A valid JSON-RPC notification has no "id" and must return None (no response)
        msg = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        res = mcp_server.handle_message(msg)
        self.assertIsNone(res)

        msg_unknown = {"jsonrpc": "2.0", "method": "telemetry/custom"}
        res_unknown = mcp_server.handle_message(msg_unknown)
        self.assertIsNone(res_unknown)

    def test_call_tool_sanitize_token_usage(self):
        # Negative prompt tokens
        res = mcp_server.call_tool("log_token_usage", {"prompt_tokens": -5, "completion_tokens": 10})
        self.assertTrue(res.get("isError"))
        self.assertIn("prompt_tokens must be a non-negative integer", res["content"][0]["text"])

        # Invalid task_id characters
        res = mcp_server.call_tool("log_token_usage", {"prompt_tokens": 100, "completion_tokens": 50, "task_id": "invalid; rm -rf"})
        self.assertTrue(res.get("isError"))
        self.assertIn("task_id contains invalid characters", res["content"][0]["text"])

    def test_call_tool_sanitize_lock_traversal(self):
        # Empty module name
        res = mcp_server.call_tool("acquire_module_lock", {"module_name": ""})
        self.assertTrue(res.get("isError"))
        self.assertIn("module_name must be a non-empty string", res["content"][0]["text"])

        # Traversal sequence
        res = mcp_server.call_tool("acquire_module_lock", {"module_name": "../etc/passwd"})
        self.assertTrue(res.get("isError"))
        self.assertIn("contains dangerous characters or path traversal sequences", res["content"][0]["text"])

        # Traversal in release
        res = mcp_server.call_tool("release_module_lock", {"module_name": "/absolute/path"})
        self.assertTrue(res.get("isError"))
        self.assertIn("contains dangerous characters or path traversal sequences", res["content"][0]["text"])

    def test_is_safe_import_path(self):
        allowed = "/home/user/project/.agents/scripts"
        self.assertTrue(mcp_server.is_safe_import_path("/home/user/project/.agents/scripts/validate.py", allowed))
        self.assertTrue(mcp_server.is_safe_import_path("/home/user/project/.agents/scripts/cli/commands/token.py", allowed))
        self.assertFalse(mcp_server.is_safe_import_path("/home/user/project/.agents/scripts/../../validate.py", allowed))
        self.assertFalse(mcp_server.is_safe_import_path("/home/user/project/other.py", allowed))

if __name__ == '__main__':
    unittest.main()
