#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-live-bind}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$ROOT/.docker-data/test-results"
mkdir -p "$OUT_DIR"

if [[ $# -eq 0 ]]; then
  echo "usage: test-in-container.sh <command...>" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/task-runner-test-$STAMP.log"
META_FILE="$OUT_DIR/task-runner-test-$STAMP.json"
CMD="$*"

set +e
docker compose -f "$ROOT/compose.yml" -f "$ROOT/compose.${MODE%%-*}.yml" exec -T task-runner sh -lc "$CMD" >"$OUT_FILE" 2>&1
EXIT_CODE=$?
set -e

cat > "$META_FILE" <<JSON
{
  "timestamp": "$STAMP",
  "service": "task-runner",
  "mode": "$MODE",
  "command": "$CMD",
  "exitCode": $EXIT_CODE,
  "outputFile": ".docker-data/test-results/$(basename "$OUT_FILE")"
}
JSON

cat "$OUT_FILE"
exit "$EXIT_CODE"
