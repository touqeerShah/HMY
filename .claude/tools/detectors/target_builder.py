from __future__ import annotations

from typing import Any


def is_dockerizable(record: dict[str, Any]) -> bool:
    commands = record.get("commands", {})
    ports = record.get("ports", [])
    framework = record.get("framework", "")
    kind = record.get("kind", "")

    if framework in {"nextjs", "express", "nestjs", "fastify", "react"}:
        return True
    if commands.get("start") or commands.get("dev") or commands.get("build"):
        return True
    if ports:
        return True
    if kind in {"worker", "backend", "frontend"}:
        return True
    return False


def infer_recommended_artifacts(app: dict[str, Any]) -> list[str]:
    artifacts = ["Dockerfile", ".dockerignore"]

    docker = app.get("docker", {})
    if docker.get("needs_compose"):
        artifacts.append("compose.yml")
    if docker.get("needs_makefile"):
        artifacts.append("Makefile")
    if docker.get("needs_entrypoint"):
        artifacts.append("docker/entrypoint.sh")

    return artifacts


def infer_app_type(app: dict[str, Any]) -> str:
    framework = app.get("framework", "")
    kind = app.get("kind", "")
    if framework == "nextjs":
        return "web"
    if kind == "worker":
        return "worker"
    if kind == "backend":
        return "api"
    return "service"


def infer_compose_plan(app: dict[str, Any]) -> dict[str, Any]:
    services = app.get("services", [])

    compose_services = [{"name": "app", "type": "application"}]
    volumes: list[str] = []
    depends_on: list[dict[str, Any]] = []

    for svc in services:
        if svc == "postgres":
            compose_services.append({
                "name": "postgres",
                "type": "database",
                "image_hint": "postgres:16",
            })
            volumes.append("postgres_data")
            depends_on.append({"service": "app", "requires": ["postgres"]})
        elif svc == "redis":
            compose_services.append({
                "name": "redis",
                "type": "cache",
                "image_hint": "redis:7",
            })
            depends_on.append({"service": "app", "requires": ["redis"]})
        elif svc == "rabbitmq":
            compose_services.append({
                "name": "rabbitmq",
                "type": "queue",
                "image_hint": "rabbitmq:3-management",
            })
            depends_on.append({"service": "app", "requires": ["rabbitmq"]})
        elif svc == "neo4j":
            compose_services.append({
                "name": "neo4j",
                "type": "graph-db",
                "image_hint": "neo4j:5",
            })
            volumes.append("neo4j_data")
            depends_on.append({"service": "app", "requires": ["neo4j"]})

    return {
        "required_services": compose_services,
        "networks": ["default"],
        "volumes": volumes,
        "depends_on": depends_on,
    }


def build_targets(apps: list[dict[str, Any]]) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []

    for app in apps:
        if not is_dockerizable(app):
            continue

        commands = app.get("commands", {})
        ports = app.get("ports", [])
        docker = app.get("docker", {})

        targets.append({
            "id": app["id"],
            "name": app["name"],
            "type": "app",
            "kind": app["kind"],
            "runtime": app["runtime"],
            "framework": app["framework"],
            "dockerizable": True,
            "closure_hint": app.get("internal_deps", []),
            "needs_compose": docker.get("needs_compose", False),
            "needs_makefile": docker.get("needs_makefile", False),
            "needs_entrypoint": docker.get("needs_entrypoint", False),
            "base_image_hint": docker.get("base_image_hint", {}),
            "packaging": {
                "app_type": infer_app_type(app),
                "expose_port": ports[0] if ports else None,
                "run_command": commands.get("start", ""),
                "dev_command": commands.get("dev", ""),
                "build_command": commands.get("build", ""),
                "output_mode": "server",
                "requires_database_at_runtime": "postgres" in app.get("services", []),
                "requires_migrations": False,
                "recommended_artifacts": infer_recommended_artifacts(app),
            },
            "compose_plan": infer_compose_plan(app),
        })

    return {
        "schema_version": "1.1",
        "targets": targets,
    }