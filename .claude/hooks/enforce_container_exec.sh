#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-}"

if [ -z "$CMD" ]; then
  exit 0
fi

lower_cmd="$(printf '%s' "$CMD" | tr '[:upper:]' '[:lower:]')"

allow_patterns=(
  "docker compose"
  "docker/commands/"
  "bash docker/commands/"
  "./docker/commands/"
  "mcp.exec_app"
  "mcp.exec_task_runner"
  "mcp.compose_logs"
  "mcp.rebuild"
)

for pattern in "${allow_patterns[@]}"; do
  if [[ "$lower_cmd" == *"$pattern"* ]]; then
    exit 0
  fi
done

block_patterns=(
  "npm test"
  "npm run test"
  "npm run dev"
  "npm run build"
  "pnpm test"
  "pnpm dev"
  "pnpm build"
  "yarn test"
  "yarn dev"
  "pytest"
  "python manage.py test"
  "python manage.py runserver"
  "python manage.py migrate"
  "celery"
  "uvicorn"
  "gunicorn"
)

for pattern in "${block_patterns[@]}"; do
  if [[ "$lower_cmd" == *"$pattern"* ]]; then
    echo "Blocked host runtime command: $CMD" >&2
    echo "Use Docker runtime MCP or docker/commands wrapper scripts instead." >&2
    exit 2
  fi
done

exit 0