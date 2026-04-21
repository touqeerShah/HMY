#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
REQUEST="${2:-}"
TARGET="${3:-}"

cd "$ROOT"

python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging

if [ -n "$TARGET" ]; then
  python3 .claude/tools/project_detector.py \
    --root "$(pwd)" \
    --mode resolve-packaging \
    --target "$TARGET" \
    --request "$REQUEST"
else
  python3 .claude/tools/project_detector.py \
    --root "$(pwd)" \
    --mode resolve-packaging \
    --request "$REQUEST"
fi