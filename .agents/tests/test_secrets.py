import sys
from unittest.mock import MagicMock

# Dynamically mock keyring if not installed to prevent patching errors
try:
    import keyring
except ImportError:
    keyring = MagicMock()
    sys.modules['keyring'] = keyring

import unittest
from unittest.mock import patch, mock_open
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import secrets

class TestSecretsModule(unittest.TestCase):
    
    @patch.dict(os.environ, {"AAC_MASTER_KEY": "test-env-key-123"})
    def test_get_master_key_env_var(self):
        # Env var takes priority
        self.assertEqual(secrets.get_master_key(), "test-env-key-123")
        
    @patch.dict(os.environ, {}, clear=True)
    @patch('keyring.get_password')
    def test_get_master_key_keyring(self, mock_get_password):
        mock_get_password.return_value = "keyring-stored-secret"
        self.assertEqual(secrets.get_master_key(), "keyring-stored-secret")
        mock_get_password.assert_called_once_with("aac-v3", "master")

    @patch.dict(os.environ, {}, clear=True)
    @patch('keyring.get_password', side_effect=Exception("Keyring failed"))
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="file-stored-key\n")
    def test_get_master_key_file(self, mock_file, mock_exists, mock_keyring):
        mock_exists.return_value = True
        key = secrets.get_master_key()
        self.assertEqual(key, "file-stored-key")

    @patch.dict(os.environ, {"AAC_MASTER_KEY": "my-passphrase"})
    def test_encryption_decryption_roundtrip(self):
        plaintext = "secret-pat-token-456"
        ciphertext = secrets.encrypt(plaintext)
        self.assertTrue(ciphertext.startswith("encrypted:"))
        
        decrypted = secrets.decrypt(ciphertext)
        self.assertEqual(decrypted, plaintext)

    def test_decrypt_non_encrypted_passthrough(self):
        plaintext = "plain-text-unmodified"
        self.assertEqual(secrets.decrypt(plaintext), plaintext)
        self.assertEqual(secrets.decrypt(None), None)
        self.assertEqual(secrets.decrypt(""), "")

if __name__ == '__main__':
    unittest.main()
