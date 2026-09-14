#!/bin/sh
# Antigravity Stop Hook: Quality Gate (POSIX sh)

INPUT=$(cat)
if [ -z "$INPUT" ]; then
  echo '{"decision":"allow"}'
  exit 0
fi

if echo "$INPUT" | grep -q '"terminationReason":"model_stop"'; then
  if ! node --test tests/memory-system.test.mjs >/dev/null 2>&1; then
    echo '{"decision":"continue","reason":"Quality Gate Failed: Unit tests are failing. Please fix regressions before concluding."}'
    exit 0
  fi
fi

echo '{"decision":"allow"}'
exit 0
