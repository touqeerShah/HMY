#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

required=(
  ".claude/cache/project_facts.json"
  ".claude/cache/packaging_plan.json"
  ".claude/cache/image_selection_report.json"
)

missing=0
for f in "${required[@]}"; do
  if [ ! -f "$f" ]; then
    missing=1
    break
  fi
done

if [ "$missing" -eq 1 ]; then
  python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
fi

if [ ! -f ".claude/cache/packaging_plan.json" ]; then
  python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
fi

if [ ! -f ".claude/cache/image_selection_report.json" ]; then
  python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
fi