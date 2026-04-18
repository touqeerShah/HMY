#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
MODE="${2:-bootstrap}"

mkdir -p "$ROOT/.claude/cache"

python3 "$ROOT/.claude/tools/project_detector.py" \
  --root "$ROOT" \
  --mode "$MODE"