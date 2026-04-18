from __future__ import annotations

from typing import Any


def build_graph(
    apps: list[dict[str, Any]],
    packages: list[dict[str, Any]],
    infra: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for app in apps:
        nodes.append({
            "id": app["id"],
            "type": "app",
            "kind": app["kind"],
            "runtime": app["runtime"],
            "framework": app["framework"],
            "path": app["path"],
        })

    for pkg in packages:
        nodes.append({
            "id": pkg["id"],
            "type": "package",
            "kind": pkg["kind"],
            "runtime": pkg["runtime"],
            "framework": pkg.get("framework", ""),
            "path": pkg["path"],
        })

    for item in infra:
        nodes.append({
            "id": item["id"],
            "type": "service",
            "kind": item["kind"],
            "service": item["name"],
        })

    package_ids = {pkg["name"]: pkg["id"] for pkg in packages}

    for app in apps:
        for dep in app.get("internal_deps", []):
            if dep in package_ids:
                edges.append({
                    "from": app["id"],
                    "to": package_ids[dep],
                    "type": "imports",
                    "strength": 1.0,
                })

        for service in app.get("services", []):
            edges.append({
                "from": app["id"],
                "to": f"infra/{service}",
                "type": "uses",
                "strength": 1.0,
            })

    return {
        "schema_version": "1.0",
        "nodes": nodes,
        "edges": edges,
    }


def graph_closure(
    graph: dict[str, Any],
    target: str,
    allowed_edge_types: set[str] | None = None,
) -> dict[str, Any]:
    allowed = allowed_edge_types or {"imports", "depends_on", "uses"}
    edges = graph.get("edges", [])
    nodes = {n["id"]: n for n in graph.get("nodes", [])}

    visited: set[str] = set()
    queue: list[str] = [target]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue

        visited.add(current)

        for edge in edges:
            if edge["from"] == current and edge["type"] in allowed:
                nxt = edge["to"]
                if nxt not in visited:
                    queue.append(nxt)

    return {
        "target": target,
        "included_nodes": [nodes[n] for n in visited if n in nodes],
        "included_edges": [
            e for e in edges
            if e["from"] in visited and e["to"] in visited and e["type"] in allowed
        ],
    }