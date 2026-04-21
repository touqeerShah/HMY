#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-live-bind}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$ROOT/.docker-data/command-output"
mkdir -p "$OUT_DIR"

if [[ $# -eq 0 ]]; then
  echo "usage: run-in-task-runner.sh <command...>" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/task-runner-run-$STAMP.log"
META_FILE="$OUT_DIR/task-runner-run-$STAMP.json"
CMD="$*"

set +e
docker compose -f "$ROOT/compose.yml" -f "$ROOT/compose.${MODE%%-*}.yml" run --rm task-runner sh -lc "$CMD" >"$OUT_FILE" 2>&1
EXIT_CODE=$?
set -e

cat > "$META_FILE" <<JSON
{
  "timestamp": "$STAMP",
  "service": "task-runner",
  "mode": "$MODE",
  "command": "$CMD",
  "exitCode": $EXIT_CODE,
  "outputFile": ".docker-data/command-output/$(basename "$OUT_FILE")"
}
JSON

cat "$OUT_FILE"
exit "$EXIT_CODE"
