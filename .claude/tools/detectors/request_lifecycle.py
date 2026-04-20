from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal


RequestClass = Literal[
    "new_packaging",
    "artifact_update",
    "artifact_regeneration",
    "read_only",
    "mode_change",
    "role_change",
    "productionization",
    "isolated_runtime_request",
]

LifecycleAction = Literal[
    "preserve",
    "wipe_and_reresolve",
    "reresolve",
    "ask",
    "reject",
]


def classify_packaging_request(
    user_request: str,
    current_plan: dict[str, Any] | None = None,
) -> RequestClass:
    text = (user_request or "").strip().lower()

    read_only_signals = [
        "explain",
        "what does",
        "why was",
        "why is",
        "inspect",
        "show plan",
        "what mean",
    ]
    artifact_update_signals = [
        "update dockerfile",
        "update compose",
        "modify dockerfile",
        "modify compose",
        "add healthcheck",
        "add logs",
        "change compose",
        "change dockerfile",
    ]
    artifact_regeneration_signals = [
        "regenerate dockerfile",
        "recreate compose",
        "rewrite dockerfile",
        "regenerate compose",
    ]
    mode_change_signals = [
        "switch to live-bind",
        "switch to rebuild-image",
        "make rebuild-image",
        "make live-bind",
        "hot reload",
    ]
    role_change_signals = [
        "add task-runner",
        "remove task-runner",
        "app only",
        "app-only",
    ]
    productionization_signals = [
        "production image",
        "production-ready",
        "production docker",
        "deployable image",
    ]
    isolated_runtime_signals = [
        "run tests in container",
        "cron in docker",
        "isolated container",
        "task-runner",
        "inside docker only",
        "not on host",
        "isolate from host",
    ]
    new_packaging_signals = [
        "dockerize",
        "create docker",
        "add compose",
        "containerize",
        "package this project",
    ]

    if any(signal in text for signal in read_only_signals):
        return "read_only"
    if any(signal in text for signal in artifact_update_signals):
        return "artifact_update"
    if any(signal in text for signal in artifact_regeneration_signals):
        return "artifact_regeneration"
    if any(signal in text for signal in mode_change_signals):
        return "mode_change"
    if any(signal in text for signal in role_change_signals):
        return "role_change"
    if any(signal in text for signal in productionization_signals):
        return "productionization"
    if any(signal in text for signal in isolated_runtime_signals):
        return "isolated_runtime_request"
    if any(signal in text for signal in new_packaging_signals):
        return "new_packaging"

    return "new_packaging"


def decide_lifecycle_action(
    request_class: RequestClass,
    current_state: str,
    stale_flag: bool,
) -> LifecycleAction:
    if request_class == "read_only":
        return "preserve"

    if current_state in {"conflicted", "invalid"}:
        if request_class == "read_only":
            return "preserve"
        return "reresolve"

    if stale_flag:
        if request_class == "read_only":
            return "preserve"
        if request_class in {"artifact_update", "artifact_regeneration"}:
            return "reresolve"
        return "wipe_and_reresolve"

    if request_class in {"artifact_update", "artifact_regeneration"}:
        return "preserve"

    if request_class in {
        "mode_change",
        "role_change",
        "productionization",
        "isolated_runtime_request",
        "new_packaging",
    }:
        return "wipe_and_reresolve"

    return "ask"


def wipe_resolved_plan(plan: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(plan)
    updated["resolved_plan"] = None
    updated["resolution_metadata"] = {}
    updated["error"] = None
    updated["state"] = "draft_only"
    return updated


def preserve_resolved_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(plan)