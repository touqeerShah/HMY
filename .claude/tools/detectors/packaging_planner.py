from __future__ import annotations

import hashlib
import json
from typing import Any

from detectors.artifact_rules import infer_rules_for_target


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def select_target(
    targets_data: dict[str, Any],
    requested_target: str | None = None,
) -> dict[str, Any]:
    targets = targets_data.get("targets", [])
    if not targets:
        raise ValueError("No dockerizable targets found")

    if requested_target:
        for target in targets:
            if target.get("id") == requested_target:
                return target
        raise ValueError(f"Requested target not found: {requested_target}")

    if len(targets) == 1:
        return targets[0]

    dockerizable = [target for target in targets if target.get("dockerizable")]
    if len(dockerizable) == 1:
        return dockerizable[0]
    if dockerizable:
        return dockerizable[0]

    raise ValueError("No selectable docker target found")


def collect_application_image(
    target: dict[str, Any],
    image_candidates: dict[str, Any],
) -> str:
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


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _build_capabilities(rules: dict[str, Any]) -> dict[str, Any]:
    return {
        "supports_compose": bool(rules.get("supports_compose", True)),
        "supports_live_bind": bool(rules.get("supports_live_bind", True)),
        "supports_rebuild_image": bool(rules.get("supports_rebuild_image", True)),
        "supports_task_runner": bool(rules.get("supports_task_runner", False)),
        "supports_host_output_dirs": bool(rules.get("supports_host_output_dirs", False)),
        "supports_command_runner": bool(rules.get("supports_command_runner", False)),
    }


def _build_defaults(rules: dict[str, Any]) -> dict[str, Any]:
    return {
        "default_mode": rules.get("default_mode", "live-bind"),
        "default_role_bias": rules.get("default_role_bias", "app-only"),
        "base_image_role": rules.get("base_image_role", "shared-base-for-app-and-task-runner"),
    }


def _build_suggested_modes(rules: dict[str, Any]) -> list[str]:
    suggested = list(rules.get("suggested_modes", []))
    if suggested:
        return _dedupe_keep_order(suggested)

    modes: list[str] = []
    if rules.get("supports_live_bind", False):
        modes.append("live-bind")
    if rules.get("supports_rebuild_image", False):
        modes.append("rebuild-image")
    return modes


def _build_suggested_roles(rules: dict[str, Any]) -> list[str]:
    suggested = list(rules.get("suggested_roles", []))
    if suggested:
        return _dedupe_keep_order(suggested)

    roles = ["app"]
    if rules.get("supports_task_runner", False):
        roles.append("task-runner")
    return roles


def _build_suggested_artifacts(target: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    suggested = list(rules.get("suggested_artifacts", []))
    if not suggested:
        suggested = ["Dockerfile", ".dockerignore"]

    if target.get("needs_makefile"):
        suggested.append("Makefile")
    if target.get("needs_entrypoint"):
        suggested.append("docker/entrypoint.sh")

    return _dedupe_keep_order(suggested)


def _compute_draft_hash(plan: dict[str, Any]) -> str:
    material = {
        "schema_version": plan.get("schema_version"),
        "target_id": plan.get("target_id"),
        "capabilities": plan.get("capabilities", {}),
        "defaults": plan.get("defaults", {}),
        "suggested_artifacts": plan.get("suggested_artifacts", []),
        "suggested_modes": plan.get("suggested_modes", []),
        "suggested_roles": plan.get("suggested_roles", []),
    }
    return hashlib.sha256(_stable_json(material).encode("utf-8")).hexdigest()


def build_packaging_plan(
    facts: dict[str, Any],
    graph: dict[str, Any],
    targets_data: dict[str, Any],
    image_candidates: dict[str, Any],
    closure: dict[str, Any] | None = None,
    requested_target: str | None = None,
) -> dict[str, Any]:
    target = select_target(targets_data, requested_target)
    packaging = target.get("packaging", {})
    rules = infer_rules_for_target(target, facts)

    capabilities = _build_capabilities(rules)
    defaults = _build_defaults(rules)
    suggested_artifacts = _build_suggested_artifacts(target, rules)
    suggested_modes = _build_suggested_modes(rules)
    suggested_roles = _build_suggested_roles(rules)

    selected_service_images = collect_service_images(target)
    selected_app_image = collect_application_image(target, image_candidates)

    plan: dict[str, Any] = {
        "schema_version": "3.0",
        "target_id": target["id"],
        "state": "draft_only",

        "target_path": target.get("path", target["id"]),
        "target_runtime": target.get("runtime", ""),
        "target_framework": target.get("framework", ""),

        "capabilities": capabilities,
        "defaults": defaults,
        "suggested_artifacts": suggested_artifacts,
        "suggested_modes": suggested_modes,
        "suggested_roles": suggested_roles,

        "resolved_plan": None,

        "draft_metadata": {
            "generated_at": None,
            "fingerprint_hash": None,
            "project_facts_generated_at": facts.get("generated_at"),
            "draft_hash": None,
            "target_id": target["id"],
        },

        "resolution_metadata": {},
        "error": None,

        # Deterministic repo-grounded hints that are useful later
        "runtime_hints": {
            "docker_strategy": rules.get("docker_strategy"),
            "install_cmd": rules.get("install_cmd", ""),
            "build_cmd": rules.get("build_cmd", packaging.get("build_command", "")),
            "start_cmd": rules.get("start_cmd", packaging.get("run_command", "")),
            "dev_cmd": rules.get("dev_cmd", packaging.get("dev_command", "")),
            "copy_outputs": rules.get("copy_outputs", []),
            "non_root": rules.get("non_root", True),
            "port": rules.get("port", packaging.get("expose_port")),
            "framework_profile": rules.get("framework_profile"),
        },

        "image_hints": {
            "application_candidate": selected_app_image,
            "service_candidates": selected_service_images,
            "base_image_role": defaults.get("base_image_role"),
        },

        "target_hints": {
            "app_type": packaging.get("app_type", "service"),
            "run_command": packaging.get("run_command", ""),
            "build_command": packaging.get("build_command", ""),
            "compose_plan": target.get("compose_plan", {}),
        },
    }

    plan["draft_metadata"]["draft_hash"] = _compute_draft_hash(plan)
    return plan