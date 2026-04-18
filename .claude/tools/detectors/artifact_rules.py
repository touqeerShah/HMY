from __future__ import annotations

from typing import Any


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
        return {
            "docker_strategy": "multi-stage",
            "install_cmd": install_cmd,
            "build_cmd": packaging.get("build_command", "npm run build"),
            "start_cmd": packaging.get("run_command", "npm start"),
            "port": packaging.get("expose_port", 3000),
            "non_root": True,
            "copy_outputs": [".next", "public", "package.json"],
        }

    return {
        "docker_strategy": "multi-stage",
        "install_cmd": install_cmd,
        "build_cmd": packaging.get("build_command", "npm run build"),
        "start_cmd": packaging.get("run_command", "npm start"),
        "port": packaging.get("expose_port", 3000),
        "non_root": True,
        "copy_outputs": ["dist", "package.json"],
    }


def infer_python_layout(target: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    packaging = target.get("packaging", {})
    return {
        "docker_strategy": "single-stage",
        "install_cmd": "pip install -r requirements.txt",
        "build_cmd": packaging.get("build_command", ""),
        "start_cmd": packaging.get("run_command", "python app.py"),
        "port": packaging.get("expose_port", 8000),
        "non_root": True,
    }


def infer_rules_for_target(target: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    runtime = target.get("runtime", "")

    if runtime == "node":
        return infer_node_layout(target, facts)
    if runtime == "python":
        return infer_python_layout(target, facts)

    return {
        "docker_strategy": "single-stage",
        "install_cmd": "",
        "build_cmd": target.get("packaging", {}).get("build_command", ""),
        "start_cmd": target.get("packaging", {}).get("run_command", ""),
        "port": target.get("packaging", {}).get("expose_port"),
        "non_root": True,
    }