from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from detectors.chunk_builder import build_chunks
from detectors.common import read_json, write_json, write_jsonl
from detectors.fingerprint import build_fingerprint
from detectors.graph_builder import build_graph, graph_closure
from detectors.image_candidates import build_image_candidates
from detectors.image_report import build_image_selection_report
from detectors.monorepo_detector import (
    classify_package_kind,
    detect_workspace_tool,
    discover_node_apps,
    repo_topology,
)
from detectors.node_detector import detect_node_app
from detectors.packaging_planner import build_packaging_plan, select_target
from detectors.target_builder import build_targets


def now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def collect_internal_deps(root: Path, app_record: dict, package_names: set[str]) -> list[str]:
    pkg = read_json(root / app_record["path"] / "package.json")
    deps = {}
    deps.update(pkg.get("dependencies", {}))
    deps.update(pkg.get("devDependencies", {}))
    return sorted(name for name in deps.keys() if name in package_names)


def build_repo_outputs(root: Path) -> tuple[dict, dict, list[dict], dict, dict, dict]:
    discovered_paths = discover_node_apps(root)
    workspace_tool = detect_workspace_tool(root)
    topology, monorepo = repo_topology(root, discovered_paths)

    detected_records: list[dict] = []
    for app_dir in discovered_paths:
        record = detect_node_app(root, app_dir)
        if record:
            detected_records.append(record)

    apps: list[dict] = []
    packages: list[dict] = []
    package_names: set[str] = set()

    for record in detected_records:
        if record["path"].startswith("packages/"):
            record["kind"] = "library"
            packages.append(record)
            package_names.add(record["name"])
        else:
            if record["path"] != ".":
                record["kind"] = classify_package_kind(Path(record["path"]))
            apps.append(record)

    for app in apps:
        app["internal_deps"] = collect_internal_deps(root, app, package_names)

    service_names = sorted({svc for app in apps for svc in app.get("services", [])})

    service_kind_map = {
        "postgres": "database",
        "mysql": "database",
        "mariadb": "database",
        "mongodb": "database",
        "redis": "cache",
        "rabbitmq": "queue",
        "kafka": "queue",
        "neo4j": "graph-db",
        "search": "search",
        "object-storage": "object-storage",
    }

    infra = [
        {
            "id": f"infra/{name}",
            "name": name,
            "kind": service_kind_map.get(name, "service"),
            "engine": name,
        }
        for name in service_names
    ]

    runtime_versions = sorted(
        {
            r.get("runtime_version", "")
            for r in detected_records
            if r.get("runtime") == "node" and r.get("runtime_version", "")
        }
    )

    facts = {
        "schema_version": "2.1",
        "generated_at": now_iso(),
        "repo": {
            "name": root.resolve().name,
            "root": ".",
            "topology": topology,
            "monorepo": monorepo,
            "workspace_tool": workspace_tool,
        },
        "runtimes": [{"family": "node", "versions": runtime_versions}],
        "apps": apps,
        "packages": packages,
        "infra": infra,
        "container_defaults": {
            "prefer_non_root": True,
            "pin_major_versions": True,
            "avoid_latest": True,
        },
    }

    graph = build_graph(apps, packages, infra)
    chunks = build_chunks(apps, packages, infra)
    fingerprint = build_fingerprint(root)
    targets = build_targets(apps)
    image_candidates = build_image_candidates(targets)

    return facts, graph, chunks, fingerprint, targets, image_candidates


def write_outputs(
    root: Path,
    facts: dict,
    graph: dict,
    chunks: list[dict],
    fingerprint: dict,
    targets: dict,
    image_candidates: dict,
) -> None:
    cache = root / ".claude" / "cache"
    write_json(cache / "project_facts.json", facts)
    write_json(cache / "project_graph.json", graph)
    write_jsonl(cache / "project_chunks.jsonl", chunks)
    write_json(cache / "project_fingerprint.json", fingerprint)
    write_json(cache / "project_targets.json", targets)
    write_json(cache / "image_candidates.json", image_candidates)


def ensure_base_outputs(root: Path) -> tuple[dict, dict, dict, dict]:
    cache = root / ".claude" / "cache"
    facts = read_json(cache / "project_facts.json")
    graph = read_json(cache / "project_graph.json")
    targets = read_json(cache / "project_targets.json")
    image_candidates = read_json(cache / "image_candidates.json")

    if not facts or not graph or not targets:
        facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
        write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)

    return facts, graph, targets, image_candidates


def handle_bootstrap(root: Path) -> int:
    facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
    write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)
    print("Project facts generated.")
    return 0


def handle_refresh(root: Path) -> int:
    cache = root / ".claude" / "cache"
    existing = read_json(cache / "project_fingerprint.json")
    new_fp = build_fingerprint(root)

    if existing.get("hash") == new_fp.get("hash"):
        print("Project facts are up to date.")
        return 0

    facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
    write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)
    print("Fingerprint changed. Project facts refreshed.")
    return 0


def handle_graph_closure(root: Path, target: str) -> int:
    cache = root / ".claude" / "cache"
    graph = read_json(cache / "project_graph.json")

    if not graph:
        facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
        write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)

    closure = graph_closure(graph, target)
    write_json(cache / "project_closure.json", closure)
    print(f"Graph closure written for target: {target}")
    return 0


def handle_list_targets(root: Path) -> int:
    cache = root / ".claude" / "cache"
    targets = read_json(cache / "project_targets.json")

    if not targets:
        facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
        write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)

    print("Detected packaging targets:")
    for item in targets.get("targets", []):
        print(f'- {item["id"]} [{item["runtime"]}/{item["framework"]}]')
    return 0


def handle_plan_packaging(root: Path, requested_target: str) -> int:
    cache = root / ".claude" / "cache"
    facts, graph, targets, image_candidates = ensure_base_outputs(root)
    closure = read_json(cache / "project_closure.json")

    plan = build_packaging_plan(
        facts=facts,
        graph=graph,
        targets_data=targets,
        image_candidates=image_candidates or {"targets": []},
        closure=closure if closure else None,
        requested_target=requested_target or None,
    )

    write_json(cache / "packaging_plan.json", plan)
    print(f'Packaging plan written for target: {plan["target_id"]}')
    return 0


def handle_write_image_report(root: Path, requested_target: str) -> int:
    cache = root / ".claude" / "cache"
    facts, graph, targets_data, image_candidates = ensure_base_outputs(root)

    packaging_plan = read_json(cache / "packaging_plan.json")
    if not packaging_plan:
        plan = build_packaging_plan(
            facts=facts,
            graph=graph,
            targets_data=targets_data,
            image_candidates=image_candidates or {"targets": []},
            closure=read_json(cache / "project_closure.json") or None,
            requested_target=requested_target or None,
        )
        write_json(cache / "packaging_plan.json", plan)
        packaging_plan = plan

    target = select_target(targets_data, requested_target or packaging_plan.get("target_id"))
    report = build_image_selection_report(
        target=target,
        packaging_plan=packaging_plan,
        image_candidates=image_candidates or {"targets": []},
        mcp_used=True,
        mcp_server="docker-hub",
        fallback_used=False,
    )
    write_json(cache / "image_selection_report.json", report)
    print(f'Image selection report written for target: {target["id"]}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument(
        "--mode",
        default="bootstrap",
        choices=[
            "bootstrap",
            "refresh",
            "graph-closure",
            "list-targets",
            "plan-packaging",
            "write-image-report",
        ],
    )
    parser.add_argument("--target", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "bootstrap":
        return handle_bootstrap(root)
    if args.mode == "refresh":
        return handle_refresh(root)
    if args.mode == "graph-closure":
        if not args.target:
            raise SystemExit("--target is required for graph-closure")
        return handle_graph_closure(root, args.target)
    if args.mode == "list-targets":
        return handle_list_targets(root)
    if args.mode == "plan-packaging":
        return handle_plan_packaging(root, args.target)
    if args.mode == "write-image-report":
        return handle_write_image_report(root, args.target)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())