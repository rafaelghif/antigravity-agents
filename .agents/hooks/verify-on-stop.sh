#!/bin/sh
# Antigravity Stop Hook: Quality Gate (POSIX sh)

INPUT=$(cat)
if [ -z "$INPUT" ]; then
  echo '{"decision":"allow"}'
  exit 0
fi

if echo "$INPUT" | grep -q '"terminationReason":"model_stop"'; then
  ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
  if [ -f "$ROOT_DIR/tests/memory-system.test.mjs" ]; then
    if ! (cd "$ROOT_DIR" && node --test tests/memory-system.test.mjs tests/cli.test.mjs >/dev/null 2>&1); then
      echo '{"decision":"continue","reason":"Quality Gate Failed: Unit tests are failing. Please fix regressions before concluding."}'
      exit 0
    fi
  fi
fi

echo '{"decision":"allow"}'
exit 0
