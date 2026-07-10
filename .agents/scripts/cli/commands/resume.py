import os
import sys

def run(args):
    flag_path = ".agents/state/paused.flag"
    if os.path.exists(flag_path):
        try:
            os.remove(flag_path)
            print("==========================================================")
            print("   Antigravity Agent Resumed [READY]                      ")
            print("==========================================================")
            print("Agent is reactivated and ready to perform tasks.")
            print("==========================================================")
        except Exception as e:
            print(f"Error removing paused flag: {e}")
    else:
        print("Agent is not currently paused.")
