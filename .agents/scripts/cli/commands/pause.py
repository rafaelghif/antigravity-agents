import os
import sys

def run(args):
    os.makedirs(".agents/state", exist_ok=True)
    with open(".agents/state/paused.flag", "w", encoding="utf-8") as f:
        f.write("1")
    print("==========================================================")
    print("   Antigravity Agent Paused [PAUSE ACTIVE]                ")
    print("==========================================================")
    print("Agent is now paused. It will not run any tasks or tools.")
    print("Run './helper.sh resume' to reactivate the agent.")
    print("==========================================================")
