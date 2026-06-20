#!/usr/bin/env bash
set -euo pipefail

PORT=${1:-3131}
PID_FILE=".server.pid"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Already running (pid $(cat "$PID_FILE")) on http://localhost:$PORT"
  exit 0
fi

npx serve -p "$PORT" . &>/tmp/prose-linter.log &
echo $! > "$PID_FILE"

echo "Prose Linter running at http://localhost:$PORT (pid $!)"
echo "Log: /tmp/prose-linter.log"
