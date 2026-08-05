---
name: verification
description: Use after edits or when debugging to detect the project stack and run the narrowest relevant verification loop.
---

Run `python3 scripts/verify.py` first. Follow only checks detected by the script. Never invent `npm test`, `pytest`, or other commands. If no project test suite exists, run structural validation and report the gap.
