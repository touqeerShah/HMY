from __future__ import annotations

from pathlib import Path

from .common import read_json


def detect_workspace_tool(root: Path) -> str | None:
    if (root / "pnpm-workspace.yaml").is_file():
        return "pnpm-workspace"
    if (root / "turbo.json").is_file():
        return "turbo"
    if (root / "nx.json").is_file():
        return "nx"

    pkg = read_json(root / "package.json")
    if "workspaces" in pkg:
        return "npm-workspaces"

    return None


def discover_node_apps(root: Path) -> list[Path]:
    candidates: list[Path] = []

    if (root / "package.json").is_file():
        candidates.append(root)

    for pattern in ["apps/*", "packages/*", "services/*"]:
        for p in root.glob(pattern):
            if p.is_dir() and (p / "package.json").is_file():
                candidates.append(p)

    unique: list[Path] = []
    seen: set[str] = set()

    for path in candidates:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(path)

    return unique


def repo_topology(root: Path, discovered_paths: list[Path]) -> tuple[str, bool]:
    if len(discovered_paths) > 1:
        return "multi-app", True

    tool = detect_workspace_tool(root)
    if tool:
        return "monorepo", True

    return "single-app", False


def classify_package_kind(path: Path) -> str:
    name = path.name.lower()

    if len(path.parts) >= 2 and path.parts[-2] == "packages":
        return "library"
    if name in {"web", "frontend", "site"}:
        return "frontend"
    if name in {"api", "backend", "server"}:
        return "backend"
    if name in {"worker", "jobs", "queue"}:
        return "worker"

    return "service"