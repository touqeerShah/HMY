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
            app_candidates = [c["image"] for c in item.get("candidates", []) if c.get("image")]
            break

    selected_app = packaging_plan["selected_images"]["application"]
    alternatives = [x for x in app_candidates if x != selected_app]

    service_images = []
    for svc_name, image in packaging_plan["selected_images"]["services"].items():
        service_images.append(
            {
                "service": svc_name,
                "selected": image,
                "source": "docker-hub-mcp" if mcp_used else "fallback-policy",
            }
        )

    return {
        "schema_version": "1.0",
        "target_id": target["id"],
        "mcp_required": True,
        "mcp_used": mcp_used,
        "mcp_server": mcp_server if mcp_used else "",
        "application_image": {
            "selected": selected_app,
            "source": "docker-hub-mcp" if mcp_used else "fallback-policy",
            "alternatives_considered": alternatives,
        },
        "service_images": service_images,
        "fallback_used": fallback_used,
        "reasoning": (
            f"Selected images based on target runtime={target.get('runtime')} "
            f"framework={target.get('framework')} and cached packaging needs."
        ),
    }