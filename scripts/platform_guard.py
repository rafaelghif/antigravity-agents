#!/usr/bin/env python3
"""
AAC Cross-Platform Platform & Standard I/O Guard.
Guarantees UTF-8 stdio and Windows compatibility across Linux, macOS, and Windows.
Automatically reconfigures sys.stdout and sys.stderr on import to prevent cp932/cp1252 UnicodeEncodeErrors.
"""
from __future__ import annotations

import io
import os
import sys

def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, io.UnsupportedOperation, OSError) as exc:
                sys.stderr.write(f"[STDIO NOTICE] Stream reconfigure notice: {exc}\n")

def get_utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env

# Auto-execute on import
configure_stdio()
