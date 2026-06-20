#!/usr/bin/env bash
set -euo pipefail

PID_FILE=".server.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No server running (no .server.pid found)"
  exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Stopped (pid $PID)"
else
  echo "Process $PID was not running"
fi

rm -f "$PID_FILE"
