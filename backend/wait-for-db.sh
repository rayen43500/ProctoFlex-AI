#!/bin/sh
# Simple wait-for-db script using python socket connect -- works in minimal images
set -e

HOST="${DB_HOST:-postgres}"
PORT="${DB_PORT:-5432}"
TIMEOUT="${DB_TIMEOUT:-60}"

echo "Waiting for database at ${HOST}:${PORT} (timeout ${TIMEOUT}s)"
i=0
while true; do
  # try to connect using python
  python - <<PY
import socket,sys
try:
    s=socket.socket()
    s.settimeout(1)
    s.connect(("${HOST}", int(${PORT})))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  if [ $? -eq 0 ]; then
    echo "Database is reachable"
    break
  fi
  i=$((i+1))
  if [ "$i" -ge "$TIMEOUT" ]; then
    echo "Timed out waiting for ${HOST}:${PORT} after ${TIMEOUT}s"
    exit 1
  fi
  sleep 1
done

exit 0
