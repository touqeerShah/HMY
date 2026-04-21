#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
shift || true

cd "$ROOT"

STATE_FILE=".claude/cache/runtime_state.json"

rebuild_required=false
restart_required=false
reasons=()

for path in "$@"; do
  case "$path" in
    Dockerfile|docker/*|compose.yml|compose.live.yml|compose.rebuild.yml)
      restart_required=true
      reasons+=("$path changed")
      ;;
    package.json|package-lock.json|pnpm-lock.yaml|yarn.lock|requirements.txt|poetry.lock|Pipfile.lock)
      rebuild_required=true
      reasons+=("$path changed")
      ;;
    .env|.env.*|next.config.*|pyproject.toml|manage.py)
      restart_required=true
      reasons+=("$path changed")
      ;;
  esac
done

cat > "$STATE_FILE" <<EOF
{
  "mode": null,
  "rebuild_required": $rebuild_required,
  "restart_required": $restart_required,
  "reasons": ["$(IFS='","'; echo "${reasons[*]}")"]
}
EOF