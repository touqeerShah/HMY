from __future__ import annotations

from typing import Any

from detectors.common import build_error


def _smallest_valid_roles(plan: dict[str, Any]) -> list[str]:
    defaults = plan.get("defaults", {}) or {}
    capabilities = plan.get("capabilities", {}) or {}

    if defaults.get("default_role_bias") == "app-only":
        return ["app"]

    if capabilities.get("supports_task_runner", False):
        return ["app"]

    return ["app"]


def _smallest_valid_modes(plan: dict[str, Any]) -> list[str]:
    defaults = plan.get("defaults", {}) or {}
    capabilities = plan.get("capabilities", {}) or {}

    preferred = defaults.get("default_mode")
    supported: list[str] = []

    if capabilities.get("supports_live_bind", False):
        supported.append("live-bind")
    if capabilities.get("supports_rebuild_image", False):
        supported.append("rebuild-image")

    if preferred and preferred in supported:
        return [preferred]
    if supported:
        return [supported[0]]

    return []


def _derive_compose_files(enabled_modes: list[str], supports_compose: bool) -> list[str]:
    if not supports_compose:
        return []

    files = ["compose.yml"]
    if "live-bind" in enabled_modes:
        files.append("compose.live.yml")
    if "rebuild-image" in enabled_modes:
        files.append("compose.rebuild.yml")
    return files


def _derive_command_scripts(enabled_roles: list[str], request_class: str) -> list[str]:
    scripts: list[str] = []

    if "task-runner" in enabled_roles:
        scripts.extend(
            [
                "docker/commands/run-in-task-runner.sh",
                "docker/commands/exec-in-task-runner.sh",
            ]
        )

    if request_class in {"isolated_runtime_request", "artifact_update"}:
        scripts.extend(
            [
                "docker/commands/run-in-container.sh",
                "docker/commands/test-in-container.sh",
                "docker/commands/logs.sh",
            ]
        )

    seen = set()
    ordered = []
    for item in scripts:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _derive_host_output_dirs(
    enabled_roles: list[str],
    request_class: str,
    capabilities: dict[str, Any],
) -> list[str]:
    if not capabilities.get("supports_host_output_dirs", False):
        return []

    if (
        request_class not in {"isolated_runtime_request", "artifact_update", "artifact_regeneration"}
        and "task-runner" not in enabled_roles
    ):
        return []

    return [
        ".docker-data/logs",
        ".docker-data/test-results",
        ".docker-data/command-output",
    ]


def _derive_artifacts(
    suggested_artifacts: list[str],
    compose_files: list[str],
    command_scripts: list[str],
    host_output_dirs: list[str],
) -> list[str]:
    items = list(suggested_artifacts) + list(compose_files) + list(command_scripts) + list(host_output_dirs)

    seen = set()
    ordered = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _validate_resolution(
    capabilities: dict[str, Any],
    enabled_roles: list[str],
    enabled_modes: list[str],
) -> dict[str, Any] | None:
    if "task-runner" in enabled_roles and not capabilities.get("supports_task_runner", False):
        return build_error(
            code="ERR_CAPABILITY_CONFLICT",
            message="Request requires task-runner, but the target does not support task-runner.",
            recoverable=True,
            suggested_action="Resolve with app-only packaging or choose a different target.",
        )

    if "live-bind" in enabled_modes and not capabilities.get("supports_live_bind", False):
        return build_error(
            code="ERR_INVALID_REQUEST_MODE",
            message="Request requires live-bind mode, but the target does not support it.",
            recoverable=True,
            suggested_action="Resolve with rebuild-image mode instead.",
        )

    if "rebuild-image" in enabled_modes and not capabilities.get("supports_rebuild_image", False):
        return build_error(
            code="ERR_INVALID_REQUEST_MODE",
            message="Request requires rebuild-image mode, but the target does not support it.",
            recoverable=True,
            suggested_action="Resolve with live-bind mode instead.",
        )

    return None


def resolve_from_request(
    plan: dict[str, Any],
    request_class: str,
    user_request: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    capabilities = plan.get("capabilities", {}) or {}
    suggested_artifacts = list(plan.get("suggested_artifacts", []) or [])

    enabled_roles = _smallest_valid_roles(plan)
    enabled_modes = _smallest_valid_modes(plan)

    text = (user_request or "").lower()

    if request_class == "productionization":
        enabled_roles = ["app"]
        enabled_modes = (
            ["rebuild-image"]
            if capabilities.get("supports_rebuild_image", False)
            else _smallest_valid_modes(plan)
        )

    elif request_class == "isolated_runtime_request":
        enabled_roles = ["task-runner"] if capabilities.get("supports_task_runner", False) else ["app"]
        enabled_modes = (
            ["rebuild-image"]
            if "rebuild" in text and capabilities.get("supports_rebuild_image", False)
            else _smallest_valid_modes(plan)
        )

    elif request_class == "mode_change":
        if "live-bind" in text:
            enabled_modes = ["live-bind"]
        elif "rebuild-image" in text or "production" in text:
            enabled_modes = ["rebuild-image"]

    elif request_class == "role_change":
        if "task-runner" in text:
            enabled_roles = ["task-runner"]
        elif "app-only" in text or "app only" in text:
            enabled_roles = ["app"]

    elif request_class == "new_packaging":
        enabled_roles = _smallest_valid_roles(plan)
        enabled_modes = _smallest_valid_modes(plan)

    validation_error = _validate_resolution(capabilities, enabled_roles, enabled_modes)
    if validation_error:
        return None, validation_error

    compose_files = _derive_compose_files(
        enabled_modes=enabled_modes,
        supports_compose=capabilities.get("supports_compose", False),
    )
    command_scripts = _derive_command_scripts(
        enabled_roles=enabled_roles,
        request_class=request_class,
    )
    host_output_dirs = _derive_host_output_dirs(
        enabled_roles=enabled_roles,
        request_class=request_class,
        capabilities=capabilities,
    )
    artifacts_to_generate = _derive_artifacts(
        suggested_artifacts=suggested_artifacts,
        compose_files=compose_files,
        command_scripts=command_scripts,
        host_output_dirs=host_output_dirs,
    )

    resolved_plan = {
        "enabled_roles": enabled_roles,
        "enabled_modes": enabled_modes,
        "artifacts_to_generate": artifacts_to_generate,
        "compose_files": compose_files,
        "command_scripts": command_scripts,
        "host_output_dirs": host_output_dirs,
        "execution_targets": list(enabled_roles),
        "image_resolution_policy": "recheck-with-mcp-before-write",
    }
    return resolved_plan, None