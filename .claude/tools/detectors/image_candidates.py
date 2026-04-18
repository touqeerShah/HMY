from __future__ import annotations

from typing import Any


def default_candidates_for_target(target: dict[str, Any]) -> dict[str, Any]:
    hint = target.get("base_image_hint", {})
    runtime = hint.get("runtime", "")
    version = hint.get("version", "")
    variant = hint.get("variant", "")

    candidates: list[dict[str, Any]] = []

    if runtime == "node":
        if version and variant:
            candidates.append({
                "image": f"node:{version}-{variant}",
                "source": "default-policy",
                "score": 0.95,
            })
        if version:
            candidates.append({
                "image": f"node:{version}-slim",
                "source": "default-policy",
                "score": 0.82,
            })

    elif runtime == "python":
        if version:
            candidates.append({
                "image": f"python:{version}-slim",
                "source": "default-policy",
                "score": 0.94,
            })

    elif runtime == "go":
        if version:
            candidates.append({
                "image": f"golang:{version}",
                "source": "default-policy",
                "score": 0.90,
            })

    elif runtime == "java":
        if version:
            candidates.append({
                "image": f"eclipse-temurin:{version}-jre",
                "source": "default-policy",
                "score": 0.93,
            })

    elif runtime == "php":
        if version:
            candidates.append({
                "image": f"php:{version}-fpm",
                "source": "default-policy",
                "score": 0.91,
            })

    elif runtime == "rust":
        candidates.append({
            "image": "debian:bookworm-slim",
            "source": "default-policy",
            "score": 0.84,
        })

    return {
        "target_id": target["id"],
        "requested": hint,
        "candidates": candidates,
    }


def build_image_candidates(targets: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "targets": [default_candidates_for_target(t) for t in targets.get("targets", [])],
    }