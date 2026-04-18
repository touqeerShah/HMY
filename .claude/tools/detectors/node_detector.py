from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import detect_env_keys, read_json, relpath, safe_read_text


def detect_package_manager(root: Path, app_dir: Path | None = None) -> str:
    base = app_dir or root

    if (root / "pnpm-lock.yaml").is_file() or (base / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (root / "yarn.lock").is_file() or (base / "yarn.lock").is_file():
        return "yarn"
    if (root / "bun.lock").is_file() or (root / "bun.lockb").is_file():
        return "bun"
    if (root / "package-lock.json").is_file() or (base / "package-lock.json").is_file():
        return "npm"

    return "npm"


def detect_node_version(root: Path) -> str:
    for rel in [".nvmrc", ".node-version"]:
        p = root / rel
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()

    pkg = read_json(root / "package.json")
    return str(pkg.get("engines", {}).get("node", "")).strip()


def detect_framework(pkg_json: dict[str, Any], app_dir: Path) -> tuple[str, float]:
    deps: dict[str, Any] = {}
    deps.update(pkg_json.get("dependencies", {}))
    deps.update(pkg_json.get("devDependencies", {}))

    if (
        (app_dir / "next.config.js").is_file()
        or (app_dir / "next.config.mjs").is_file()
        or (app_dir / "next.config.ts").is_file()
    ):
        return "nextjs", 0.98

    if "next" in deps:
        return "nextjs", 0.96
    if "@nestjs/core" in deps:
        return "nestjs", 0.95
    if "express" in deps:
        return "express", 0.90
    if "fastify" in deps:
        return "fastify", 0.88
    if "react" in deps:
        return "react", 0.75

    return "node-app", 0.50


def detect_ports(framework: str) -> list[int]:
    if framework in {"nextjs", "express", "nestjs", "fastify"}:
        return [3000]
    return []


def detect_env_info(app_dir: Path) -> tuple[list[str], list[str]]:
    env_files: list[str] = []
    env_keys: list[str] = []

    for rel in [".env.example", ".env.local.example", ".env"]:
        p = app_dir / rel
        if p.is_file():
            env_files.append(rel)
            env_keys.extend(detect_env_keys(p.read_text(encoding="utf-8")))

    return sorted(set(env_files)), sorted(set(env_keys))


def detect_services(app_dir: Path) -> list[str]:
    files: list[Path] = []

    for rel in [".env.example", ".env.local.example", ".env", "package.json"]:
        p = app_dir / rel
        if p.is_file():
            files.append(p)

    for sub in ["src", "app", "pages", "server", "api", "lib"]:
        d = app_dir / sub
        if d.is_dir():
            files.extend(
                x for x in d.rglob("*")
                if x.is_file() and x.suffix in {".js", ".ts", ".tsx", ".mjs", ".cjs"}
            )

    text = "\n".join(safe_read_text(p) for p in files)

    found: list[str] = []

    if any(token in text for token in ["DATABASE_URL", "postgres://", "postgresql://", "@prisma/client", '"pg"', "'pg'"]):
        found.append("postgres")
    if any(token in text for token in ["REDIS_URL", "redis://", "ioredis", '"redis"', "'redis'"]):
        found.append("redis")
    if any(token in text for token in ["MONGODB_URI", "MONGO_URL", "mongodb://", "mongodb+srv://", "mongoose"]):
        found.append("mongodb")
    if any(token in text for token in ["RABBITMQ", "amqp://", "amqplib"]):
        found.append("rabbitmq")
    if any(token in text for token in ["neo4j://", "NEO4J_", "neo4j-driver"]):
        found.append("neo4j")
    if any(token in text for token in ["KAFKA_", "kafkajs", "9092"]):
        found.append("kafka")
    if any(token in text for token in ["ELASTICSEARCH_", "OPENSEARCH_", "@elastic/elasticsearch", "opensearch"]):
        found.append("search")
    if any(token in text for token in ["S3_", "AWS_S3_", "minio", "@aws-sdk/client-s3"]):
        found.append("object-storage")

    return sorted(set(found))


def build_commands(package_manager: str, pkg_json: dict[str, Any]) -> dict[str, str]:
    scripts = pkg_json.get("scripts", {})

    install = {
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn install --frozen-lockfile",
        "bun": "bun install --frozen-lockfile",
        "npm": "npm ci",
    }.get(package_manager, "npm ci")

    return {
        "install": install,
        "build": str(scripts.get("build", "")),
        "dev": str(scripts.get("dev", "")),
        "start": str(scripts.get("start", "")),
        "test": str(scripts.get("test", "")),
    }


def detect_lockfile(root: Path, app_dir: Path) -> str:
    for rel in ["pnpm-lock.yaml", "yarn.lock", "package-lock.json", "bun.lock", "bun.lockb"]:
        if (root / rel).is_file():
            return rel
        if (app_dir / rel).is_file():
            return rel
    return ""


def detect_node_app(root: Path, app_dir: Path) -> dict[str, Any] | None:
    pkg_path = app_dir / "package.json"
    if not pkg_path.is_file():
        return None

    pkg = read_json(pkg_path)
    framework, confidence = detect_framework(pkg, app_dir)
    package_manager = detect_package_manager(root, app_dir)
    node_version = detect_node_version(root)
    ports = detect_ports(framework)
    env_files, env_keys = detect_env_info(app_dir)
    services = detect_services(app_dir)

    rel = relpath(app_dir, root)
    name = str(pkg.get("name") or (root.resolve().name if rel == "." else app_dir.name))

    kind = "frontend" if framework in {"nextjs", "react"} else "backend"

    return {
        "id": rel,
        "name": name,
        "path": rel,
        "kind": kind,
        "runtime": "node",
        "runtime_version": node_version,
        "framework": framework,
        "framework_confidence": confidence,
        "package_manager": package_manager,
        "lockfile": detect_lockfile(root, app_dir),
        "commands": build_commands(package_manager, pkg),
        "ports": ports,
        "env_files": env_files,
        "env_keys": env_keys,
        "services": services,
        "docker": {
            "recommended": True,
            "strategy": "multi-stage",
            "base_image_hint": {
                "runtime": "node",
                "version": node_version or "20",
                "variant": "bookworm-slim",
                "official_only": True,
                "avoid_latest": True,
            },
            "needs_compose": bool(services),
            "needs_makefile": bool(services),
            "needs_entrypoint": False,
        },
    }