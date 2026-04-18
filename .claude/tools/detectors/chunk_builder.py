from __future__ import annotations


def build_chunks(
    apps: list[dict],
    packages: list[dict],
    infra: list[dict],
) -> list[dict]:
    rows: list[dict] = []

    for app in apps:
        service_text = ", ".join(app.get("services", [])) or "no external services detected"
        rows.append({
            "id": f'{app["id"]}:summary',
            "path": app["path"],
            "type": "app_summary",
            "text": (
                f'{app["framework"]} {app["kind"]} app at {app["path"]} '
                f'using {app["runtime"]}. Services: {service_text}.'
            ),
        })

    for pkg in packages:
        rows.append({
            "id": f'{pkg["id"]}:summary',
            "path": pkg["path"],
            "type": "package_summary",
            "text": (
                f'Internal package {pkg["name"]} at {pkg["path"]} '
                f'using {pkg["runtime"]}.'
            ),
        })

    for item in infra:
        rows.append({
            "id": f'{item["id"]}:summary',
            "path": item["id"],
            "type": "service_summary",
            "text": f'Infrastructure service {item["name"]} of kind {item["kind"]}.',
        })

    return rows