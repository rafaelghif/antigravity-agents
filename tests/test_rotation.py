#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import tempfile

# Helper paths
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(REPO_DIR, ".agents")
API_KEYS_PATH = os.path.join(AGENTS_DIR, "api_keys")
ACTIVE_KEYS_PATH = os.path.join(AGENTS_DIR, "active_api_keys")
ACTIVE_KEYS_PS1_PATH = os.path.join(AGENTS_DIR, "active_api_keys.ps1")
ACTIVE_PROFILE_PATH = os.path.join(AGENTS_DIR, "active_api_profile_name")
TOKEN_BUDGET_PATH = os.path.join(AGENTS_DIR, "token_budget.json")

TEST_FILES = [
    API_KEYS_PATH,
    ACTIVE_KEYS_PATH,
    ACTIVE_KEYS_PS1_PATH,
    ACTIVE_PROFILE_PATH,
    TOKEN_BUDGET_PATH
]

def run_mock_command(always_fail=False):
    """
    Executes the mock command behavior inside wrapper.
    Reads current active profile and exits accordingly.
    """
    profile = "unknown"
    if os.path.exists(ACTIVE_PROFILE_PATH):
        with open(ACTIVE_PROFILE_PATH, "r") as f:
            profile = f.read().strip()
            
    print(f"[MOCK-COMMAND] Active Profile: {profile}")
    
    if always_fail:
        print(f"[MOCK-COMMAND] Simulating exhaustion failure for profile '{profile}'...")
        sys.exit(429)
        
    if profile == "mock_p1":
        print("[MOCK-COMMAND] Simulating rate limit (HTTP 429) on first profile...")
        sys.exit(429)
    elif profile == "mock_p2":
        print("[MOCK-COMMAND] Simulating success on second rotated profile!")
        sys.exit(0)
    else:
        print(f"[MOCK-COMMAND] Profile '{profile}' fallback exit code 0...")
        sys.exit(0)

def setup_mock_config():
    """
    Creates temporary mock api_keys file with two profiles.
    """
    print("Setting up mock API keys configuration...")
    mock_keys_content = """# Mock API Keys
mock_p1.GEMINI_API_KEY=AIzaSy_mock_key_p1
mock_p1.OPENAI_API_KEY=sk-proj-mock_key_p1
mock_p2.GEMINI_API_KEY=AIzaSy_mock_key_p2
mock_p2.OPENAI_API_KEY=sk-proj-mock_key_p2
"""
    with open(API_KEYS_PATH, "w") as f:
        f.write(mock_keys_content)
        
    # Set active profile initially to mock_p1
    with open(ACTIVE_PROFILE_PATH, "w") as f:
        f.write("mock_p1")
        
    # Write empty active_api_keys
    with open(ACTIVE_KEYS_PATH, "w") as f:
        f.write("# active keys\nexport GEMINI_API_KEY=\"AIzaSy_mock_key_p1\"\n")

def run_bash_wrapper_test():
    """
    Runs tests against api-rotate-wrapper.sh
    """
    wrapper_path = os.path.join(AGENTS_DIR, "scripts", "api-rotate-wrapper.sh")
    if not os.path.exists(wrapper_path):
        print(f"Error: Bash wrapper not found at {wrapper_path}")
        return False
        
    print("\n=== Test 1: Bash Wrapper - Successful Rotation ===")
    setup_mock_config()
    
    # Run: wrapper.sh python3 tests/test_rotation.py --mock-command
    cmd = [wrapper_path, sys.executable, __file__, "--mock-command"]
    print(f"Running: {' '.join(cmd)}")
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("Stdout:")
    print(proc.stdout)
    print("Stderr:")
    print(proc.stderr)
    print(f"Exit Code: {proc.returncode}")
    
    # Assert wrapper succeeded
    assert proc.returncode == 0, "Wrapper failed to execute successfully"
    # Assert output contains rotation warning
    assert "Rotating API profile" in proc.stdout, "Wrapper did not print rotation warning"
    # Assert active profile was updated to mock_p2
    with open(ACTIVE_PROFILE_PATH, "r") as f:
        final_profile = f.read().strip()
    assert final_profile == "mock_p2", f"Active profile should be mock_p2, got {final_profile}"
    print("[PASS] Successful Rotation Test succeeded!")
    
    print("\n=== Test 2: Bash Wrapper - Profile Exhaustion ===")
    setup_mock_config()
    
    # Run: wrapper.sh python3 tests/test_rotation.py --mock-command-always-fail
    cmd = [wrapper_path, sys.executable, __file__, "--mock-command-always-fail"]
    print(f"Running: {' '.join(cmd)}")
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("Stdout:")
    print(proc.stdout)
    print("Stderr:")
    print(proc.stderr)
    print(f"Exit Code: {proc.returncode}")
    
    # Assert wrapper failed with 429 or 173 (modulo 256)
    assert proc.returncode in (429, 173), f"Wrapper exit code should be 429 or 173, got {proc.returncode}"
    # Assert output contains exhaustion warning
    assert "All available API profiles exhausted" in proc.stderr or "All available API profiles exhausted" in proc.stdout, "Wrapper did not print exhaustion warning"
    print("[PASS] Profile Exhaustion Test succeeded!")
    
    return True

def main():
    # Parse mock command execution
    if "--mock-command" in sys.argv:
        run_mock_command(always_fail=False)
        return
    elif "--mock-command-always-fail" in sys.argv:
        run_mock_command(always_fail=True)
        return

    print("==========================================================")
    # 1. Back up existing configuration files
    backups = {}
    print("Backing up existing configurations...")
    for path in TEST_FILES:
        if os.path.exists(path):
            print(f"  Backing up: {os.path.basename(path)}")
            with open(path, "r", encoding="utf-8") as f:
                backups[path] = f.read()
            os.remove(path)
            
    success = False
    try:
        # 2. Run tests
        success = run_bash_wrapper_test()
        
        # 3. Skip PowerShell wrapper on non-Windows/non-PowerShell systems
        print("\n=== Test 3: PowerShell Wrapper Execution Check ===")
        ps_wrapper_path = os.path.join(AGENTS_DIR, "scripts", "api-rotate-wrapper.ps1")
        if os.path.exists(ps_wrapper_path):
            print(f"[INFO] PowerShell wrapper exists at {ps_wrapper_path}")
            print("Skipping active PowerShell execution check (no powershell/pwsh in this system).")
        else:
            print(f"[FAIL] PowerShell wrapper does not exist at {ps_wrapper_path}!")
            success = False
            
    except Exception as e:
        print(f"\n[ERROR] Test runner crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        # 4. Teardown and restore files
        print("\nRestoring original configurations...")
        for path in TEST_FILES:
            if os.path.exists(path):
                os.remove(path)
            if path in backups:
                print(f"  Restoring: {os.path.basename(path)}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(backups[path])
        print("==========================================================")
        
    if success:
        print("\nALL TEST CASES PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nTESTS FAILED OR DEGRADED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
