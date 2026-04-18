from __future__ import annotations

import hashlib
from pathlib import Path

IMPORTANT_FILES = [
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "pnpm-workspace.yaml",
    "turbo.json",
    "nx.json",
    ".nvmrc",
    ".node-version",
    ".env.example",
    ".env.local.example",
    "Dockerfile",
    "docker/Dockerfile",
    "compose.yml",
    "compose.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
]


def collect_fingerprint_files(root: Path) -> list[str]:
    files: list[str] = []

    for rel in IMPORTANT_FILES:
        p = root / rel
        if p.is_file():
            files.append(rel)

    for pattern in [
        "apps/*/package.json",
        "packages/*/package.json",
        "services/*/package.json",
    ]:
        for p in root.glob(pattern):
            if p.is_file():
                files.append(str(p.relative_to(root)).replace("\\", "/"))

    return sorted(set(files))


def compute_hash(root: Path, files: list[str]) -> str:
    h = hashlib.sha256()
    for rel in files:
        p = root / rel
        if not p.is_file():
            continue
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def build_fingerprint(root: Path) -> dict:
    files = collect_fingerprint_files(root)
    return {
        "schema_version": "1.0",
        "strategy": "hash-selected-files",
        "files": files,
        "hash": compute_hash(root, files),
    }