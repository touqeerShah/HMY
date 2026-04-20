from __future__ import annotations

from typing import Any


def _common_capabilities_defaults(
    *,
    default_mode: str,
    base_image_role: str,
    suggested_modes: list[str],
    suggested_roles: list[str],
    suggested_artifacts: list[str],
    install_cmd: str,
    build_cmd: str,
    start_cmd: str,
    dev_cmd: str,
    port: int | None,
    copy_outputs: list[str],
    docker_strategy: str,
    framework_profile: str,
) -> dict[str, Any]:
    return {
        # Capabilities
        "supports_compose": True,
        "supports_live_bind": True,
        "supports_rebuild_image": True,
        "supports_task_runner": True,
        "supports_host_output_dirs": True,
        "supports_command_runner": True,

        # Defaults
        "default_mode": default_mode,
        "default_role_bias": "app-only",
        "base_image_role": base_image_role,

        # Suggestions
        "suggested_modes": list(suggested_modes),
        "suggested_roles": list(suggested_roles),
        "suggested_artifacts": list(suggested_artifacts),

        # Runtime/build hints
        "docker_strategy": docker_strategy,
        "install_cmd": install_cmd,
        "build_cmd": build_cmd,
        "start_cmd": start_cmd,
        "dev_cmd": dev_cmd,
        "port": port,
        "non_root": True,
        "copy_outputs": list(copy_outputs),
        "framework_profile": framework_profile,

        # Non-activating hints
        "suggested_host_output_dir_names": [
            ".docker-data/logs",
            ".docker-data/test-results",
            ".docker-data/command-output",
        ],
        "default_command_runner_context": "app",
        "task_runner_default_cmd": "sh",
        "default_task_runner_mount_project": True,
        "default_task_runner_network_access": True,
        "task_runner_image_strategy": "shared-base-image",
    }


def infer_node_layout(target: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    framework = target.get("framework", "")
    packaging = target.get("packaging", {})
    package_manager = target.get("package_manager", "npm")

    install_cmd = {
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn install --frozen-lockfile",
        "bun": "bun install --frozen-lockfile",
        "npm": "npm ci",
    }.get(package_manager, "npm ci")

    if framework == "nextjs":
        return _common_capabilities_defaults(
            default_mode="live-bind",
            base_image_role="shared-base-for-app-and-task-runner",
            suggested_modes=["live-bind", "rebuild-image"],
            suggested_roles=["app", "task-runner"],
            suggested_artifacts=["Dockerfile", ".dockerignore", "compose.yml"],
            install_cmd=install_cmd,
            build_cmd=packaging.get("build_command", "npm run build"),
            start_cmd=packaging.get("run_command", "npm start"),
            dev_cmd=packaging.get("dev_command", "npm run dev"),
            port=packaging.get("expose_port", 3000),
            copy_outputs=[".next", "public", "package.json"],
            docker_strategy="multi-stage",
            framework_profile="nextjs",
        )

    return _common_capabilities_defaults(
        default_mode="live-bind",
        base_image_role="shared-base-for-app-and-task-runner",
        suggested_modes=["live-bind", "rebuild-image"],
        suggested_roles=["app", "task-runner"],
        suggested_artifacts=["Dockerfile", ".dockerignore", "compose.yml"],
        install_cmd=install_cmd,
        build_cmd=packaging.get("build_command", "npm run build"),
        start_cmd=packaging.get("run_command", "npm start"),
        dev_cmd=packaging.get("dev_command", "npm run dev"),
        port=packaging.get("expose_port", 3000),
        copy_outputs=["dist", "package.json"],
        docker_strategy="multi-stage",
        framework_profile="node-generic",
    )


def infer_python_layout(target: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    packaging = target.get("packaging", {})

    return _common_capabilities_defaults(
        default_mode="live-bind",
        base_image_role="shared-base-for-app-and-task-runner",
        suggested_modes=["live-bind", "rebuild-image"],
        suggested_roles=["app", "task-runner"],
        suggested_artifacts=["Dockerfile", ".dockerignore", "compose.yml"],
        install_cmd="pip install -r requirements.txt",
        build_cmd=packaging.get("build_command", ""),
        start_cmd=packaging.get("run_command", "python app.py"),
        dev_cmd=packaging.get("dev_command", "python app.py"),
        port=packaging.get("expose_port", 8000),
        copy_outputs=[],
        docker_strategy="single-stage",
        framework_profile="python-generic",
    )


def infer_rules_for_target(target: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    runtime = target.get("runtime", "")
    packaging = target.get("packaging", {})

    if runtime == "node":
        return infer_node_layout(target, facts)

    if runtime == "python":
        return infer_python_layout(target, facts)

    return _common_capabilities_defaults(
        default_mode="live-bind",
        base_image_role="shared-base-for-app-and-task-runner",
        suggested_modes=["live-bind", "rebuild-image"],
        suggested_roles=["app"],
        suggested_artifacts=["Dockerfile", ".dockerignore"],
        install_cmd="",
        build_cmd=packaging.get("build_command", ""),
        start_cmd=packaging.get("run_command", ""),
        dev_cmd=packaging.get("dev_command", packaging.get("run_command", "")),
        port=packaging.get("expose_port"),
        copy_outputs=[],
        docker_strategy="single-stage",
        framework_profile="generic-runtime",
    )