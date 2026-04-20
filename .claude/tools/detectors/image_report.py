from __future__ import annotations

from typing import Any


def build_image_selection_report(
    target: dict[str, Any],
    packaging_plan: dict[str, Any],
    image_candidates: dict[str, Any],
    mcp_used: bool = True,
    mcp_server: str = "docker-hub",
    fallback_used: bool = False,
) -> dict[str, Any]:
    app_candidates: list[str] = []

    for item in image_candidates.get("targets", []):
        if item.get("target_id") == target["id"]:
            app_candidates = [
                candidate["image"]
                for candidate in item.get("candidates", [])
                if candidate.get("image")
            ]
            break

    image_hints = packaging_plan.get("image_hints", {})
    defaults = packaging_plan.get("defaults", {})
    capabilities = packaging_plan.get("capabilities", {})
    resolved_plan = packaging_plan.get("resolved_plan") or {}

    selected_app = image_hints.get("application_candidate", "")
    alternatives = [image for image in app_candidates if image != selected_app]

    service_images = []
    for service_name, image in (image_hints.get("service_candidates", {}) or {}).items():
        service_images.append(
            {
                "service": service_name,
                "selected": image,
                "source": "docker-hub-mcp" if mcp_used else "fallback-policy",
            }
        )

    roles_supported = ["app", "task-runner"] if capabilities.get("supports_task_runner", False) else ["app"]

    workflow_modes_supported: list[str] = []
    if capabilities.get("supports_live_bind", False):
        workflow_modes_supported.append("live-bind")
    if capabilities.get("supports_rebuild_image", False):
        workflow_modes_supported.append("rebuild-image")

    roles_active = list(resolved_plan.get("enabled_roles", [])) if resolved_plan else []
    workflow_modes_active = list(resolved_plan.get("enabled_modes", [])) if resolved_plan else []

    base_image_role = defaults.get(
        "base_image_role",
        image_hints.get("base_image_role", "shared-base-for-app-and-task-runner"),
    )

    return {
        "schema_version": "3.0",
        "target_id": target["id"],
        "mcp_preferred": True,
        "mcp_used": mcp_used,
        "mcp_server": mcp_server if mcp_used else "",
        "roles_supported": roles_supported,
        "roles_active": roles_active,
        "workflow_modes_supported": workflow_modes_supported,
        "workflow_modes_active": workflow_modes_active,
        "base_image_role": base_image_role,
        "application_image": {
            "selected": selected_app,
            "source": "docker-hub-mcp" if mcp_used else "fallback-policy",
            "alternatives_considered": alternatives,
        },
        "service_images": service_images,
        "fallback_used": fallback_used,
        "reasoning": (
            f"Selected image support for target runtime={target.get('runtime')} "
            f"framework={target.get('framework')} using "
            f"{'docker-hub MCP' if mcp_used else 'fallback policy from cached candidates'}, "
            f"with roles_supported={roles_supported} and "
            f"workflow_modes_supported={workflow_modes_supported}."
        ),
    }