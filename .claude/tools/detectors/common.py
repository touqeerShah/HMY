from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def detect_env_keys(text: str) -> list[str]:
    keys: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.append(key)
    return sorted(set(keys))


def is_nonempty_dict(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def build_error(
    code: str,
    message: str,
    recoverable: bool,
    suggested_action: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error = {
        "code": code,
        "message": message,
        "recoverable": recoverable,
        "suggested_action": suggested_action,
    }
    if details:
        error["details"] = details
    return error


def with_error_state(
    plan: dict[str, Any],
    *,
    state: str,
    code: str,
    message: str,
    recoverable: bool,
    suggested_action: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    updated = dict(plan or {})
    updated["state"] = state
    updated["error"] = build_error(
        code=code,
        message=message,
        recoverable=recoverable,
        suggested_action=suggested_action,
        details=details,
    )
    return updated