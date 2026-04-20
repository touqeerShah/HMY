from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from detectors.common import build_error


MATERIAL_CAPABILITY_KEYS = [
    "supports_compose",
    "supports_live_bind",
    "supports_rebuild_image",
    "supports_task_runner",
    "supports_host_output_dirs",
    "supports_command_runner",
]

MATERIAL_DEFAULT_KEYS = [
    "default_mode",
    "default_role_bias",
    "base_image_role",
]


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def extract_material_draft_fields(plan: dict[str, Any]) -> dict[str, Any]:
    capabilities = plan.get("capabilities", {}) or {}
    defaults = plan.get("defaults", {}) or {}

    material_capabilities = {
        key: capabilities.get(key)
        for key in MATERIAL_CAPABILITY_KEYS
        if key in capabilities
    }
    material_defaults = {
        key: defaults.get(key)
        for key in MATERIAL_DEFAULT_KEYS
        if key in defaults
    }

    return {
        "schema_version": plan.get("schema_version"),
        "target_id": plan.get("target_id"),
        "capabilities": material_capabilities,
        "defaults": material_defaults,
        "suggested_artifacts": list(plan.get("suggested_artifacts", []) or []),
        "suggested_modes": list(plan.get("suggested_modes", []) or []),
        "suggested_roles": list(plan.get("suggested_roles", []) or []),
    }


def compute_draft_hash(plan: dict[str, Any]) -> str:
    material = extract_material_draft_fields(plan)
    return hashlib.sha256(_stable_json(material).encode("utf-8")).hexdigest()


def _compare_section(
    current: dict[str, Any],
    previous: dict[str, Any],
    key: str,
    reason: str,
    reasons: list[str],
) -> None:
    if current.get(key) != previous.get(key):
        reasons.append(reason)


def is_plan_stale(
    current_draft: dict[str, Any],
    previous_plan: dict[str, Any],
    current_fingerprint_hash: str | None = None,
    previous_fingerprint_hash: str | None = None,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if not previous_plan:
        return True, ["missing_previous_plan"]

    _compare_section(current_draft, previous_plan, "schema_version", "schema_changed", reasons)
    _compare_section(current_draft, previous_plan, "target_id", "target_changed", reasons)

    current_material = extract_material_draft_fields(current_draft)
    previous_material = extract_material_draft_fields(previous_plan)

    if current_material.get("capabilities") != previous_material.get("capabilities"):
        reasons.append("capabilities_changed")

    if current_material.get("defaults") != previous_material.get("defaults"):
        reasons.append("defaults_changed")

    if current_material.get("suggested_artifacts") != previous_material.get("suggested_artifacts"):
        reasons.append("suggested_artifacts_changed")

    if current_material.get("suggested_modes") != previous_material.get("suggested_modes"):
        reasons.append("suggested_modes_changed")

    if current_material.get("suggested_roles") != previous_material.get("suggested_roles"):
        reasons.append("suggested_roles_changed")

    current_hash = current_draft.get("draft_metadata", {}).get("draft_hash") or compute_draft_hash(current_draft)
    previous_hash = previous_plan.get("draft_metadata", {}).get("draft_hash")

    if previous_hash and current_hash != previous_hash:
        reasons.append("draft_hash_changed")

    if (
        current_fingerprint_hash
        and previous_fingerprint_hash
        and current_fingerprint_hash != previous_fingerprint_hash
    ):
        reasons.append("fingerprint_changed")

    return (len(reasons) > 0, reasons)


def mark_plan_stale(plan: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    updated = deepcopy(plan)
    updated["state"] = "stale"
    updated["error"] = build_error(
        code="ERR_STALE_PLAN",
        message="Resolved plan is stale and must be re-resolved before artifact generation.",
        recoverable=True,
        suggested_action="Re-resolve packaging intent against the current draft plan.",
        details={"reasons": list(reasons)},
    )
    return updated