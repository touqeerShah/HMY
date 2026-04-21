#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-live-bind}"
TAIL="${TAIL:-200}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$ROOT/.docker-data/logs"
mkdir -p "$OUT_DIR"

if [[ $# -lt 1 ]]; then
  echo "usage: logs.sh <service>" >&2
  exit 1
fi

SERVICE="$1"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/${SERVICE}-logs-$STAMP.log"

docker compose -f "$ROOT/compose.yml" -f "$ROOT/compose.${MODE%%-*}.yml" logs --tail "$TAIL" "$SERVICE" | tee "$OUT_FILE"
