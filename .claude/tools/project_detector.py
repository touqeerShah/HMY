from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from detectors.chunk_builder import build_chunks
from detectors.common import build_error, read_json, write_json, write_jsonl
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
from detectors.plan_resolver import resolve_from_request
from detectors.plan_staleness import is_plan_stale, mark_plan_stale
from detectors.request_lifecycle import (
    classify_packaging_request,
    decide_lifecycle_action,
    preserve_resolved_plan,
    wipe_resolved_plan,
)
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


def ensure_base_outputs(root: Path) -> tuple[dict, dict, dict, dict, dict]:
    cache = root / ".claude" / "cache"
    facts = read_json(cache / "project_facts.json")
    graph = read_json(cache / "project_graph.json")
    targets = read_json(cache / "project_targets.json")
    image_candidates = read_json(cache / "image_candidates.json")
    fingerprint = read_json(cache / "project_fingerprint.json")

    if not facts or not graph or not targets or not image_candidates or not fingerprint:
        facts, graph, chunks, fingerprint, targets, image_candidates = build_repo_outputs(root)
        write_outputs(root, facts, graph, chunks, fingerprint, targets, image_candidates)

    return facts, graph, targets, image_candidates, fingerprint


def ensure_closure_for_target(root: Path, graph: dict, target_id: str) -> dict:
    cache = root / ".claude" / "cache"
    closure = read_json(cache / "project_closure.json")

    if not closure or closure.get("target_id") != target_id:
        closure = graph_closure(graph, target_id)
        if isinstance(closure, dict) and "target_id" not in closure:
            closure["target_id"] = target_id
        write_json(cache / "project_closure.json", closure)

    return closure


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
    if isinstance(closure, dict) and "target_id" not in closure:
        closure["target_id"] = target

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
    facts, graph, targets, image_candidates, fingerprint = ensure_base_outputs(root)

    selected = select_target(targets, requested_target or None)
    target_id = selected["id"]
    closure = ensure_closure_for_target(root, graph, target_id)

    plan = build_packaging_plan(
        facts=facts,
        graph=graph,
        targets_data=targets,
        image_candidates=image_candidates,
        closure=closure,
        requested_target=target_id,
    )
    plan["target_id"] = target_id
    plan["draft_metadata"]["generated_at"] = now_iso()
    plan["draft_metadata"]["fingerprint_hash"] = fingerprint.get("hash")

    write_json(cache / "packaging_plan.json", plan)
    print(f"Packaging draft written for target: {target_id}")
    return 0


def handle_resolve_packaging(root: Path, requested_target: str, user_request: str) -> int:
    cache = root / ".claude" / "cache"
    facts, graph, targets, image_candidates, fingerprint = ensure_base_outputs(root)

    previous_plan = read_json(cache / "packaging_plan.json")
    if not previous_plan:
        handle_plan_packaging(root, requested_target)
        previous_plan = read_json(cache / "packaging_plan.json")

    if not previous_plan:
        invalid_plan = {
            "schema_version": "3.0",
            "target_id": requested_target or "",
            "state": "invalid",
            "capabilities": {},
            "defaults": {},
            "suggested_artifacts": [],
            "suggested_modes": [],
            "suggested_roles": [],
            "resolved_plan": None,
            "draft_metadata": {},
            "resolution_metadata": {},
            "error": build_error(
                code="ERR_CACHE_MISSING",
                message="Packaging draft could not be created.",
                recoverable=False,
                suggested_action="Regenerate draft inputs before resolving packaging.",
            ),
        }
        write_json(cache / "packaging_plan.json", invalid_plan)
        raise SystemExit("Packaging draft could not be created")

    required_plan_keys = [
        "schema_version",
        "target_id",
        "state",
        "capabilities",
        "defaults",
        "suggested_artifacts",
        "suggested_modes",
        "suggested_roles",
        "draft_metadata",
    ]
    missing = [key for key in required_plan_keys if key not in previous_plan]
    if missing:
        previous_plan["state"] = "invalid"
        previous_plan["error"] = build_error(
            code="ERR_REQUIRED_FIELD_MISSING",
            message="Packaging draft is missing required keys.",
            recoverable=False,
            suggested_action="Regenerate the packaging draft before resolving.",
            details={"missing_keys": missing},
        )
        write_json(cache / "packaging_plan.json", previous_plan)
        raise SystemExit("Packaging draft is missing required keys")

    selected = select_target(targets, requested_target or previous_plan.get("target_id"))
    target_id = selected["id"]
    closure = ensure_closure_for_target(root, graph, target_id)

    fresh_draft = build_packaging_plan(
        facts=facts,
        graph=graph,
        targets_data=targets,
        image_candidates=image_candidates,
        closure=closure,
        requested_target=target_id,
    )
    fresh_draft["target_id"] = target_id
    fresh_draft["draft_metadata"]["generated_at"] = now_iso()
    fresh_draft["draft_metadata"]["fingerprint_hash"] = fingerprint.get("hash")

    stale_flag, stale_reasons = is_plan_stale(
        current_draft=fresh_draft,
        previous_plan=previous_plan,
        current_fingerprint_hash=fingerprint.get("hash"),
        previous_fingerprint_hash=previous_plan.get("draft_metadata", {}).get("fingerprint_hash"),
    )

    working_plan = fresh_draft
    if stale_flag:
        working_plan = mark_plan_stale(fresh_draft, stale_reasons)
    elif previous_plan.get("resolved_plan") is not None:
        working_plan["resolved_plan"] = previous_plan.get("resolved_plan")
        working_plan["resolution_metadata"] = previous_plan.get("resolution_metadata", {})

    request_class = classify_packaging_request(user_request, working_plan)
    lifecycle_action = decide_lifecycle_action(
        request_class=request_class,
        current_state=working_plan.get("state", "draft_only"),
        stale_flag=stale_flag,
    )

    if lifecycle_action == "preserve":
        working_plan = preserve_resolved_plan(working_plan)

    elif lifecycle_action in {"wipe_and_reresolve", "reresolve"}:
        if lifecycle_action == "wipe_and_reresolve":
            working_plan = wipe_resolved_plan(working_plan)

        resolved_plan, error = resolve_from_request(
            plan=working_plan,
            request_class=request_class,
            user_request=user_request,
        )

        if error:
            working_plan["state"] = "conflicted"
            working_plan["error"] = error
            working_plan["resolved_plan"] = None
            working_plan["resolution_metadata"] = {}
            write_json(cache / "packaging_plan.json", working_plan)
            raise SystemExit(error["message"])

        working_plan["resolved_plan"] = resolved_plan
        working_plan["state"] = "resolved"
        working_plan["error"] = None
        working_plan["resolution_metadata"] = {
            "resolved_at": now_iso(),
            "resolved_from_request": user_request,
            "used_defaults": request_class in {"new_packaging", "productionization"},
            "clarification_required": False,
            "resolution_source": {
                "modes": "mixed",
                "roles": "mixed",
                "artifacts": "derived-from-enabled-modes-and-roles",
            },
        }

    elif lifecycle_action == "ask":
        working_plan["state"] = "conflicted"
        working_plan["error"] = build_error(
            code="ERR_RESOLUTION_AMBIGUOUS",
            message="Request is materially ambiguous and needs one clarifying question.",
            recoverable=True,
            suggested_action="Ask one focused question before resolving packaging.",
        )
        write_json(cache / "packaging_plan.json", working_plan)
        raise SystemExit("Request is ambiguous and needs clarification")

    elif lifecycle_action == "reject":
        working_plan["state"] = "conflicted"
        working_plan["error"] = build_error(
            code="ERR_CAPABILITY_CONFLICT",
            message="Request could not be resolved safely against current capabilities.",
            recoverable=True,
            suggested_action="Adjust the request or choose a compatible target.",
        )
        write_json(cache / "packaging_plan.json", working_plan)
        raise SystemExit("Request conflicts with current packaging capabilities")

    write_json(cache / "packaging_plan.json", working_plan)
    print(f'Packaging resolved for target: {working_plan.get("target_id")}')
    return 0


def handle_write_image_report(root: Path, requested_target: str) -> int:
    cache = root / ".claude" / "cache"
    _, _, targets_data, image_candidates, _ = ensure_base_outputs(root)

    packaging_plan = read_json(cache / "packaging_plan.json")
    if not packaging_plan:
        handle_plan_packaging(root, requested_target)
        packaging_plan = read_json(cache / "packaging_plan.json")

    if not packaging_plan:
        raise SystemExit("Unable to create packaging draft")

    required_plan_keys = [
        "schema_version",
        "target_id",
        "state",
        "capabilities",
        "defaults",
        "suggested_artifacts",
        "suggested_modes",
        "suggested_roles",
        "draft_metadata",
    ]
    missing = [key for key in required_plan_keys if key not in packaging_plan]
    if missing:
        raise SystemExit(f"Packaging draft missing required keys: {', '.join(missing)}")

    target = select_target(targets_data, requested_target or packaging_plan.get("target_id"))
    report = build_image_selection_report(
        target=target,
        packaging_plan=packaging_plan,
        image_candidates=image_candidates,
        mcp_used=False,
        mcp_server="",
        fallback_used=True,
    )
    report["generated_at"] = now_iso()
    report["target_id"] = target["id"]

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
            "resolve-packaging",
            "write-image-report",
        ],
    )
    parser.add_argument("--target", default="")
    parser.add_argument("--request", default="")
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
    if args.mode == "resolve-packaging":
        return handle_resolve_packaging(root, args.target, args.request)
    if args.mode == "write-image-report":
        return handle_write_image_report(root, args.target)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())