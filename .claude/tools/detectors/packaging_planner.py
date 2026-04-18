from __future__ import annotations

from typing import Any


def select_target(targets_data: dict[str, Any], requested_target: str | None = None) -> dict[str, Any]:
    targets = targets_data.get("targets", [])
    if not targets:
        raise ValueError("No dockerizable targets found")

    if requested_target:
        for t in targets:
            if t.get("id") == requested_target:
                return t
        raise ValueError(f"Requested target not found: {requested_target}")

    if len(targets) == 1:
        return targets[0]

    dockerizable = [t for t in targets if t.get("dockerizable")]
    if len(dockerizable) == 1:
        return dockerizable[0]
    if dockerizable:
        return dockerizable[0]

    raise ValueError("No selectable docker target found")


def collect_application_image(target: dict[str, Any], image_candidates: dict[str, Any]) -> str:
    for item in image_candidates.get("targets", []):
        if item.get("target_id") == target["id"]:
            candidates = item.get("candidates", [])
            if candidates:
                return candidates[0]["image"]

    hint = target.get("base_image_hint", {})
    runtime = hint.get("runtime", "")
    version = hint.get("version", "")
    variant = hint.get("variant", "")

    if runtime == "node":
        return f"node:{version or '20'}-{variant}" if variant else f"node:{version or '20'}-slim"
    if runtime == "python":
        return f"python:{version or '3.12'}-slim"
    if runtime == "go":
        return f"golang:{version or '1.23'}"
    if runtime == "java":
        return f"eclipse-temurin:{version or '21'}-jre"
    if runtime == "php":
        return f"php:{version or '8.3'}-fpm"
    if runtime == "rust":
        return "debian:bookworm-slim"
    return "ubuntu:24.04"


def collect_service_images(target: dict[str, Any]) -> dict[str, str]:
    selected: dict[str, str] = {}
    compose_plan = target.get("compose_plan", {})

    for svc in compose_plan.get("required_services", []):
        name = svc.get("name")
        if not name or name == "app":
            continue
        hint = svc.get("image_hint")
        if hint:
            selected[name] = hint

    return selected


def compute_artifacts(target: dict[str, Any]) -> list[str]:
    artifacts = ["Dockerfile", ".dockerignore"]
    if target.get("needs_compose"):
        artifacts.append("compose.yml")
    if target.get("needs_makefile"):
        artifacts.append("Makefile")
    if target.get("needs_entrypoint"):
        artifacts.append("docker/entrypoint.sh")
    return artifacts


def build_packaging_plan(
    facts: dict[str, Any],
    graph: dict[str, Any],
    targets_data: dict[str, Any],
    image_candidates: dict[str, Any],
    closure: dict[str, Any] | None = None,
    requested_target: str | None = None,
) -> dict[str, Any]:
    target = select_target(targets_data, requested_target)

    selected_app_image = collect_application_image(target, image_candidates)
    selected_service_images = collect_service_images(target)

    closure_nodes: list[str] = []
    if closure and closure.get("target") == target["id"]:
        closure_nodes = [n.get("id") for n in closure.get("included_nodes", []) if n.get("id")]

    if not closure_nodes:
        closure_nodes = [target["id"]]
        for svc_name in selected_service_images.keys():
            closure_nodes.append(f"infra/{svc_name}")

    packaging = target.get("packaging", {})
    compose_plan = target.get("compose_plan", {})

    return {
        "schema_version": "1.0",
        "target_id": target["id"],
        "target_path": target["id"],
        "target_runtime": target.get("runtime", ""),
        "target_framework": target.get("framework", ""),
        "selected_images": {
            "application": selected_app_image,
            "services": selected_service_images,
        },
        "closure_nodes": closure_nodes,
        "artifacts_to_generate": compute_artifacts(target),
        "compose_services": [svc["name"] for svc in compose_plan.get("required_services", []) if svc.get("name")],
        "entrypoint_required": bool(target.get("needs_entrypoint")),
        "makefile_required": bool(target.get("needs_makefile")),
        "port": packaging.get("expose_port"),
        "run_command": packaging.get("run_command", ""),
        "build_command": packaging.get("build_command", ""),
        "app_type": packaging.get("app_type", "service"),
        "compose_plan": compose_plan,
    }

