from __future__ import annotations

from typing import Any

from detectors.common import build_error


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


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


def _derive_compose_files(
    enabled_modes: list[str],
    supports_compose: bool,
) -> list[str]:
    if not supports_compose:
        return []

    files = ["compose.yml"]
    if "live-bind" in enabled_modes:
        files.append("compose.live.yml")
    if "rebuild-image" in enabled_modes:
        files.append("compose.rebuild.yml")
    return files


def _needs_runtime_execution(user_request: str, request_class: str) -> bool:
    text = (user_request or "").lower()
    runtime_terms = [
        "run",
        "test",
        "check",
        "debug",
        "migrate",
        "migration",
        "scrape",
        "cron",
        "inside docker",
        "not on host",
        "build",
        "start",
        "dev",
        "job",
        "integration",
    ]
    return request_class in {"isolated_runtime_request"} or any(
        term in text for term in runtime_terms
    )


def _needs_isolation(user_request: str, request_class: str) -> bool:
    text = (user_request or "").lower()
    isolation_terms = [
        "isolated",
        "task-runner",
        "not on host",
        "inside docker",
        "scrape",
        "migration",
        "migrate",
        "cron",
        "job",
        "integration",
        "browser automation",
        "third-party",
    ]
    return request_class == "isolated_runtime_request" or any(
        term in text for term in isolation_terms
    )


def _needs_observation(user_request: str, request_class: str) -> bool:
    text = (user_request or "").lower()
    observation_terms = [
        "log",
        "logs",
        "result",
        "results",
        "output",
        "debug",
        "inspect",
        "trace",
        "test",
        "check",
        "report",
    ]
    return request_class in {"isolated_runtime_request", "artifact_regeneration"} or any(
        term in text for term in observation_terms
    )


def _derive_command_scripts(
    enabled_roles: list[str],
    request_class: str,
    capabilities: dict[str, Any],
    user_request: str,
) -> list[str]:
    if not capabilities.get("supports_command_runner", False):
        return []

    text = (user_request or "").lower()
    scripts: list[str] = []

    runtime_like = request_class in {
        "isolated_runtime_request",
        "artifact_regeneration",
    }

    needs_logs = any(
        word in text for word in ["log", "logs", "debug", "inspect", "trace"]
    )
    needs_tests = any(
        word in text for word in ["test", "pytest", "jest", "integration", "coverage"]
    )
    needs_app_exec = any(
        word in text for word in ["run", "build", "start", "dev", "shell", "check"]
    )
    needs_task_exec = "task-runner" in enabled_roles or any(
        word in text
        for word in [
            "job",
            "cron",
            "scrape",
            "integration",
            "migrate",
            "migration",
            "isolated",
            "not on host",
            "inside docker",
        ]
    )

    if needs_app_exec or runtime_like:
        scripts.append("docker/commands/run-in-container.sh")

    if needs_tests:
        scripts.append("docker/commands/test-in-container.sh")

    if needs_logs:
        scripts.append("docker/commands/logs.sh")

    if needs_task_exec:
        scripts.extend(
            [
                "docker/commands/run-in-task-runner.sh",
                "docker/commands/exec-in-task-runner.sh",
            ]
        )

    return _dedupe_keep_order(scripts)


def _derive_host_output_dirs(
    enabled_roles: list[str],
    request_class: str,
    capabilities: dict[str, Any],
    user_request: str,
) -> list[str]:
    if not capabilities.get("supports_host_output_dirs", False):
        return []

    text = (user_request or "").lower()

    wants_observation = request_class in {
        "isolated_runtime_request",
        "artifact_regeneration",
    } or any(
        word in text
        for word in [
            "log",
            "logs",
            "test",
            "result",
            "results",
            "output",
            "debug",
            "inspect",
            "trace",
            "report",
            "check",
        ]
    )

    if not wants_observation and "task-runner" not in enabled_roles:
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
    items = (
        list(suggested_artifacts)
        + list(compose_files)
        + list(command_scripts)
        + list(host_output_dirs)
    )
    return _dedupe_keep_order(items)


def _derive_runtime_tools(
    runtime_exec_role: str,
    isolated_exec_role: str,
    observability_enabled: bool,
) -> dict[str, str]:
    tools = {
        "app_exec": "mcp.exec_app" if runtime_exec_role == "app" else "mcp.exec_task_runner",
        "task_exec": "mcp.exec_task_runner"
        if isolated_exec_role == "task-runner"
        else "mcp.exec_app",
    }

    if observability_enabled:
        tools["logs"] = "mcp.compose_logs"
        tools["output"] = "mcp.read_container_output"

    return tools


def _validate_resolution(
    capabilities: dict[str, Any],
    enabled_roles: list[str],
    enabled_modes: list[str],
) -> dict[str, Any] | None:
    if "task-runner" in enabled_roles and not capabilities.get(
        "supports_task_runner", False
    ):
        return build_error(
            code="ERR_CAPABILITY_CONFLICT",
            message="Request requires task-runner, but the target does not support task-runner.",
            recoverable=True,
            suggested_action="Resolve with app-only packaging or choose a different target.",
        )

    if "live-bind" in enabled_modes and not capabilities.get(
        "supports_live_bind", False
    ):
        return build_error(
            code="ERR_INVALID_REQUEST_MODE",
            message="Request requires live-bind mode, but the target does not support it.",
            recoverable=True,
            suggested_action="Resolve with rebuild-image mode instead.",
        )

    if "rebuild-image" in enabled_modes and not capabilities.get(
        "supports_rebuild_image", False
    ):
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
        enabled_roles = (
            ["app", "task-runner"]
            if capabilities.get("supports_task_runner", False)
            else ["app"]
        )
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
        if "task-runner" in text and capabilities.get("supports_task_runner", False):
            enabled_roles = ["app", "task-runner"]
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
        capabilities=capabilities,
        user_request=user_request,
    )
    host_output_dirs = _derive_host_output_dirs(
        enabled_roles=enabled_roles,
        request_class=request_class,
        capabilities=capabilities,
        user_request=user_request,
    )
    artifacts_to_generate = _derive_artifacts(
        suggested_artifacts=suggested_artifacts,
        compose_files=compose_files,
        command_scripts=command_scripts,
        host_output_dirs=host_output_dirs,
    )

    needs_runtime_execution = _needs_runtime_execution(user_request, request_class)
    needs_isolation = _needs_isolation(user_request, request_class)
    needs_observation = _needs_observation(user_request, request_class)

    runtime_exec_role = "app"
    if needs_isolation and "task-runner" in enabled_roles:
        runtime_exec_role = "task-runner"

    isolated_exec_role = "task-runner" if "task-runner" in enabled_roles else "app"
    observability_enabled = bool(host_output_dirs) and needs_observation

    runtime_tools = _derive_runtime_tools(
        runtime_exec_role=runtime_exec_role,
        isolated_exec_role=isolated_exec_role,
        observability_enabled=observability_enabled,
    )

    resolved_plan = {
        "enabled_roles": enabled_roles,
        "enabled_modes": enabled_modes,
        "artifacts_to_generate": artifacts_to_generate,
        "compose_files": compose_files,
        "command_scripts": command_scripts,
        "host_output_dirs": host_output_dirs,
        "execution_targets": list(enabled_roles),
        "execution_policy": "container-first",
        "runtime_exec_role": runtime_exec_role if needs_runtime_execution else "app",
        "isolated_exec_role": isolated_exec_role,
        "observability_enabled": observability_enabled,
        "output_root": "/workspace/.docker-data" if host_output_dirs else None,
        "runtime_tools": runtime_tools,
        "image_resolution_policy": "recheck-with-mcp-before-write",
    }
    return resolved_plan, None