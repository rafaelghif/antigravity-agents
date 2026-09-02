#!/usr/bin/env bash
set -e

echo "[L9 SYSTEM] Starting Enterprise Agentic Loop..."

# 1. Start the meeting coordinator in the background
if pgrep -f "meeting_coordinator.py" > /dev/null; then
    echo "Meeting coordinator is already running."
else
    python3 scripts/meeting_coordinator.py > .agents/inbox/coordinator.log 2>&1 &
    echo "Started background meeting coordinator (PID: $!)."
fi

# 2. Run the autonomous loop manager
python3 scripts/autonomous_loop.py
