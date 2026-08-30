#!/usr/bin/env python3
"""
AAC Upgrade Engine wrapper.
This delegates to the universal install.py script at the root.
"""
import sys
from pathlib import Path

# Add root directory to sys.path so we can import install
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

try:
    import install
except ImportError as e:
    sys.stderr.write(f"Error: Could not import install.py from {root_dir}\n")
    sys.exit(1)

if __name__ == "__main__":
    # We modify sys.argv slightly if we want it to behave explicitly as upgrader,
    # but the universal installer handles both based on current_version == "0.0.0".
    install.main()
