import sys
import os

# Dynamic proxy pattern to resolve standard library 'secrets' while avoiding name shadowing in python paths
std_secrets = None
if 'secrets' in sys.modules:
    # Save reference to current module to avoid recursion
    our_module = sys.modules['secrets']
    del sys.modules['secrets']
    sys_path_backup = sys.path[:]
    try:
        # Filter out directories containing "commands"
        sys.path = [p for p in sys.path if "commands" not in p.split(os.sep)]
        import secrets as system_secrets
        std_secrets = system_secrets
    except Exception:
        pass
    finally:
        sys.path = sys_path_backup
        sys.modules['secrets'] = our_module
else:
    sys_path_backup = sys.path[:]
    try:
        sys.path = [p for p in sys.path if "commands" not in p.split(os.sep)]
        import secrets as system_secrets
        std_secrets = system_secrets
    except Exception:
        pass
    finally:
        sys.path = sys_path_backup

if std_secrets:
    globals().update({k: v for k, v in std_secrets.__dict__.items() if not k.startswith('__')})

import base64
import hashlib
from cryptography.fernet import Fernet

def get_master_key() -> str:
    # 1. Check env var
    env_key = os.environ.get("AAC_MASTER_KEY")
    if env_key:
        return env_key

    # 2. Check keyring
    try:
        import keyring
        keyring_key = keyring.get_password("aac-v3", "master")
        if keyring_key:
            return keyring_key
    except Exception:
        pass

    # 3. Check fallback file
    key_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../state/master.key"))
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    # If missing, create one
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    new_key = None

    # Prompt user if interactive, and not in unit testing/CI context
    is_interactive = sys.stdin.isatty() and not os.environ.get("IN_AUDIT_TEST") and "unittest" not in sys.modules and "pytest" not in sys.modules and os.environ.get("CI") != "true"
    if is_interactive:
        try:
            import getpass
            print("AAC V3 Master Key is missing.")
            p1 = getpass.getpass("Enter new Master Key/Passphrase: ").strip()
            if p1:
                new_key = p1
                # Try to store in keyring
                try:
                    import keyring
                    keyring.set_password("aac-v3", "master", new_key)
                    print("[OK] Master Key stored in system keyring.")
                except Exception:
                    pass
        except Exception:
            pass

    if not new_key:
        # Auto-generate if non-interactive or prompt skipped
        new_key = base64.b64encode(os.urandom(32)).decode('utf-8')

    # Save to key_file with 0600 permissions
    try:
        if os.name != 'nt':
            fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with open(fd, "w", encoding="utf-8") as f:
                f.write(new_key)
        else:
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(new_key)
            try:
                os.chmod(key_file, 0o600)
            except Exception:
                pass
    except Exception:
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(new_key)
        try:
            os.chmod(key_file, 0o600)
        except Exception:
            pass

    return new_key

def _get_fernet() -> Fernet:
    master_key = get_master_key()
    # Deriving urlsafe base64 32-byte key using SHA-256
    hashed = hashlib.sha256(master_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(hashed)
    return Fernet(fernet_key)

def encrypt(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    fernet = _get_fernet()
    encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
    return f"encrypted:{encrypted_bytes.decode('utf-8')}"

def decrypt(ciphertext: str) -> str:
    if not ciphertext or not ciphertext.startswith("encrypted:"):
        return ciphertext
    token = ciphertext[len("encrypted:"):]
    fernet = _get_fernet()
    try:
        decrypted_bytes = fernet.decrypt(token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
