# Packaging System Architecture

**Recommended location in project:**
```text
./ARCHITECTURE.md
```

This document defines the Docker packaging system architecture, lifecycle, schema, resolver behavior, artifact derivation rules, and test strategy.

It reflects the current model:

- deterministic detector
- deterministic draft planner
- structured stale-plan guard
- structured request lifecycle
- resolver-owned activation
- support-vs-activation image reporting
- artifact generation only from `resolved_plan`

---

# 1. Objective

Refactor the packaging system from a policy-heavy planner into a capability-aware draft system with request-aware resolution.

The design separates three concerns:

1. **What the repo supports**
2. **What is reasonable by default**
3. **What this specific request activates**

The system should remain deterministic where possible, and only use resolver logic for request-sensitive activation.

---

# 2. Target Architecture

## 2.1 Layer 1 — Detector

The detector remains fully deterministic.

Its job is to discover facts about the repo, such as:

- runtimes
- frameworks
- services
- targets
- likely commands
- packaging hints
- infra dependencies

It does not decide active packaging behavior.

It answers only:

- what exists
- what is likely supported
- what can be packaged

---

## 2.2 Layer 2 — Draft planner

The planner is a **structured draft generator**, not a final plan generator.

It emits:

- capabilities
- suggested artifact families
- suggested roles
- suggested modes
- safe defaults
- draft metadata
- deterministic runtime and image hints

It does not decide the final active packaging output for a specific request.

More precisely:

> The detector and draft planner may emit supported capabilities, suggested artifact families, and minimally required base artifacts, but they do not decide the final active artifact set for a specific request.

---

## 2.3 Layer 3 — Resolver

The resolver turns the draft into a concrete plan for the current request.

This is the only layer that decides:

- which roles are active
- which workflow modes are active
- which concrete files should be generated
- whether wrappers/output dirs are needed
- whether to preserve, wipe, or re-resolve a prior plan

This layer is request-sensitive by design.

---

# 3. File and Module Layout

## 3.1 Core controller

```text
.claude/tools/project_detector.py
```

Responsibilities:

- bootstrap deterministic cache
- refresh deterministic cache
- write draft packaging plan
- write image selection report
- resolve request into `resolved_plan`

---

## 3.2 Detector modules

```text
.claude/tools/detectors/common.py
.claude/tools/detectors/fingerprint.py
.claude/tools/detectors/monorepo_detector.py
.claude/tools/detectors/node_detector.py
.claude/tools/detectors/target_builder.py
.claude/tools/detectors/graph_builder.py
.claude/tools/detectors/chunk_builder.py
.claude/tools/detectors/image_candidates.py
.claude/tools/detectors/artifact_rules.py
.claude/tools/detectors/packaging_planner.py
.claude/tools/detectors/plan_staleness.py
.claude/tools/detectors/request_lifecycle.py
.claude/tools/detectors/plan_resolver.py
.claude/tools/detectors/image_report.py
```

---

## 3.3 Cache files

```text
.claude/cache/project_facts.json
.claude/cache/project_graph.json
.claude/cache/project_targets.json
.claude/cache/project_chunks.jsonl
.claude/cache/project_fingerprint.json
.claude/cache/project_closure.json
.claude/cache/image_candidates.json
.claude/cache/packaging_plan.json
.claude/cache/image_selection_report.json
```

---

# 4. Phase 0 — Governance Rules

## 4.1 Schema ownership rules

Each top-level section has one owner.

| Section | Owner | Notes |
|---|---|---|
| `capabilities` | Planner | Resolver must not mutate |
| `defaults` | Planner | Resolver must not mutate |
| `suggested_artifacts` | Planner | Suggestions only |
| `suggested_modes` | Planner | Suggestions only |
| `suggested_roles` | Planner | Suggestions only |
| `resolved_plan` | Resolver | Rewritten per packaging resolution |
| `draft_metadata` | Planner/controller | Derived from deterministic inputs |
| `resolution_metadata` | Resolver | Created only when resolution occurs |
| `error` | Planner/controller/resolver | Depends on failure stage |
| `state` | Controller/resolver | Reflects lifecycle state |

### Ownership rules

- Planner writes draft sections only.
- Resolver writes resolved sections only.
- Resolver must never modify `capabilities`, `defaults`, or `suggested_*`.
- Planner must never write `resolved_plan`.
- Controller may set `state` and attach `error` during validation or recovery.

---

## 4.2 Request classification set

Every incoming packaging-related request must be classified into exactly one category before resolution logic runs.

### Allowed request classes

- `new_packaging`
- `artifact_update`
- `artifact_regeneration`
- `read_only`
- `mode_change`
- `role_change`
- `productionization`
- `isolated_runtime_request`

---

## 4.3 Material vs non-material changes

### Material changes
Any of these mark prior resolution as stale:

- `target_id` changed
- runtime changed
- framework changed
- compose capability changed
- task-runner capability changed
- supported roles changed
- supported modes changed
- host output capability changed
- command runner capability changed
- default mode changed
- base image role changed
- image capability/support family changed in a way that affects resolved usage
- planner schema version changed
- artifact family suggestions changed in a way that invalidates resolved artifacts

### Non-material changes
These do not mark resolution stale by themselves:

- timestamp changes only
- wording-only changes in notes
- ordering-only changes in lists/maps
- explanatory notes only
- non-functional metadata formatting changes

---

## 4.4 Cache recovery order

Use one deterministic recovery flow.

### Recovery sequence

1. Read required cache files.
2. If missing, regenerate deterministic draft inputs once.
3. Re-read.
4. If corrupt, regenerate once.
5. Re-read.
6. If still missing or corrupt, set:
   - `state = invalid`
   - structured cache error
7. Do not continue to resolution until draft inputs are valid.

---

## 4.5 Ambiguity bias rule

When request intent is vague, resolver must choose the smallest valid plan.

Prefer:

- one target
- one mode
- app-only
- no task-runner
- no wrapper scripts
- no host output dirs
- no split compose files
- minimal artifact set

unless the request or defaults clearly justify expansion.

---

# 5. Schema v3

## 5.1 Top-level schema

```json
{
  "schema_version": "3.0",
  "target_id": ".",
  "state": "draft_only",
  "capabilities": {},
  "defaults": {},
  "suggested_artifacts": [],
  "suggested_modes": [],
  "suggested_roles": [],
  "resolved_plan": null,
  "draft_metadata": {},
  "resolution_metadata": {},
  "error": null
}
```

---

## 5.2 `capabilities`

Describes what the repo supports.

Example:

```json
{
  "supports_compose": true,
  "supports_live_bind": true,
  "supports_rebuild_image": true,
  "supports_task_runner": true,
  "supports_host_output_dirs": true,
  "supports_command_runner": true
}
```

Rules:

- Booleans describe support, not activation.
- No active roles or active modes belong here.

---

## 5.3 `defaults`

Describes safe preference hints only.

Example:

```json
{
  "default_mode": "live-bind",
  "default_role_bias": "app-only",
  "base_image_role": "shared-base-for-app-and-task-runner"
}
```

Rules:

- Defaults help when user intent is incomplete.
- Defaults must not directly create files.
- Defaults must not activate roles or modes.

---

## 5.4 `suggested_*`

Planner suggestions only:

- `suggested_artifacts`
- `suggested_modes`
- `suggested_roles`

These are repo-grounded hints, not active packaging output.

---

## 5.5 `resolved_plan`

Only created by resolver.

Example:

```json
{
  "enabled_roles": ["app"],
  "enabled_modes": ["rebuild-image"],
  "artifacts_to_generate": [
    "Dockerfile",
    ".dockerignore",
    "compose.yml",
    "compose.rebuild.yml"
  ],
  "compose_files": [
    "compose.yml",
    "compose.rebuild.yml"
  ],
  "command_scripts": [],
  "host_output_dirs": [],
  "execution_targets": ["app"],
  "image_resolution_policy": "recheck-with-mcp-before-write"
}
```

Rules:

- This is the only valid source for artifact generation.
- Must be wiped and rebuilt according to lifecycle rules.
- Concrete files live here, not in draft sections.

---

## 5.6 `draft_metadata`

Used for stale-plan checks.

Required fields:

- `generated_at`
- `fingerprint_hash`
- `project_facts_generated_at`
- `draft_hash`
- `target_id`

---

## 5.7 `resolution_metadata`

Created when a resolution exists.

Recommended fields:

- `resolved_at`
- `resolved_from_request`
- `used_defaults`
- `clarification_required`
- `resolution_source`

---

## 5.8 `error`

Structured failure payload.

Shape:

```json
{
  "code": "ERR_CAPABILITY_CONFLICT",
  "message": "Request asked for live-bind task-runner, but task-runner is not supported for this target.",
  "recoverable": true,
  "suggested_action": "Ask user whether rebuild-image app-only packaging is acceptable."
}
```

Optional:
- `details`

---

## 5.9 Allowed state values

- `draft_only`
- `resolved`
- `stale`
- `conflicted`
- `invalid`

---

# 6. Structured Error Model

## 6.1 Error codes

Use this canonical set:

- `ERR_NO_TARGETS`
- `ERR_TARGET_NOT_FOUND`
- `ERR_CAPABILITY_CONFLICT`
- `ERR_INVALID_REQUEST_MODE`
- `ERR_INVALID_REQUEST_ROLE`
- `ERR_STALE_PLAN`
- `ERR_CACHE_MISSING`
- `ERR_CACHE_CORRUPT`
- `ERR_IMAGE_SELECTION_STALE`
- `ERR_IMAGE_SELECTION_CONFLICT`
- `ERR_RESOLUTION_AMBIGUOUS`
- `ERR_REQUIRED_FIELD_MISSING`

---

## 6.2 State transitions

### `stale`
Use when prior resolved state is not safe to reuse.

### `conflicted`
Use when request conflicts with capabilities or cannot be resolved safely.

### `invalid`
Use when cache/schema/required inputs are missing or malformed.

---

# 7. Deterministic Stale-Plan Guard

The stale guard compares:

- fresh draft vs previous cached plan
- `schema_version`
- `target_id`
- material `capabilities`
- material `defaults`
- `suggested_artifacts`
- `suggested_modes`
- `suggested_roles`
- `draft_hash`
- fingerprint hash

It must never compare a plan to itself when testing staleness.

---

# 8. Request Lifecycle

## 8.1 Request classes

- `new_packaging`
- `artifact_update`
- `artifact_regeneration`
- `read_only`
- `mode_change`
- `role_change`
- `productionization`
- `isolated_runtime_request`

## 8.2 Lifecycle actions

- `preserve`
- `wipe_and_reresolve`
- `reresolve`
- `ask`
- `reject`

## 8.3 Rules

### Preserve
Use existing valid resolved plan for:
- read-only
- narrow updates
- regeneration inside same valid scope

### Wipe and re-resolve
Use for:
- new packaging
- mode change
- role change
- productionization
- isolated runtime request

### Re-resolve
Use for:
- stale state
- conflict recovery
- updates when previous resolved state is no longer safe

### Ask
Only when a single focused clarifying question is necessary.

### Reject
When the request conflicts with supported capabilities or required inputs are invalid.

---

# 9. Resolver-Owned Activation

`plan_resolver.py` activates only from:

- current draft
- request class
- raw user request

It outputs only `resolved_plan`.

It validates:

- role support
- mode support
- compose support
- host output support
- command runner support

Generation must happen only from `resolved_plan`.

---

# 10. Artifact Derivation Rules

Artifact derivation must be reproducible from:

- `resolved_plan.enabled_roles`
- `resolved_plan.enabled_modes`
- request class
- `capabilities`
- base artifact suggestions as seed input only

## 10.1 Base artifacts

Always start from the minimal base set:

- `Dockerfile`
- `.dockerignore`

Add only when justified:

- `Makefile`
- `docker/entrypoint.sh`

---

## 10.2 Compose derivation

If compose support exists:

- always include `compose.yml`

If `live-bind` is enabled:

- include `compose.live.yml`

If `rebuild-image` is enabled:

- include `compose.rebuild.yml`

Rules:

- `live-bind` ⇒ likely `compose.live.yml`
- `rebuild-image` ⇒ likely `compose.rebuild.yml`
- both modes enabled ⇒ include both overlays
- no compose support ⇒ none

---

## 10.3 Task-runner derivation

If `task-runner` is active:

Likely include:

- `docker/commands/run-in-task-runner.sh`
- `docker/commands/exec-in-task-runner.sh`

If `task-runner` is not active:

- do not generate task-runner wrappers

Support alone is not enough; the role must be active.

---

## 10.4 Host output dir derivation

Enable host output dirs only when the request implies:

- logs
- test results
- command output
- runtime inspection
- isolated execution with observable results

Standard dirs:

- `.docker-data/logs`
- `.docker-data/test-results`
- `.docker-data/command-output`

Support alone is not enough.

---

## 10.5 Command wrapper derivation

General wrappers:

- `docker/commands/run-in-container.sh`
- `docker/commands/test-in-container.sh`
- `docker/commands/logs.sh`

Enable only when justified by request:
- in-container execution
- test running
- logs capture
- isolated runtime

Task-runner wrappers only when `task-runner` is active.

---

## 10.6 Productionization rule

For production-oriented requests, prefer the smallest valid artifact set.

Likely include:

- `Dockerfile`
- `.dockerignore`
- `compose.yml` if needed
- `compose.rebuild.yml` if rebuild-image is active

Do not automatically include:

- `compose.live.yml`
- task-runner wrappers
- host output dirs
- generic execution wrappers

---

## 10.7 Live-bind rule

If `live-bind` is enabled, likely include:

- `compose.yml`
- `compose.live.yml`

Do not automatically include:

- task-runner wrappers
- host output dirs

unless separately justified.

### Live-bind observability rule

Live-bind changes how code reaches the container, but it does not by itself guarantee visibility into what happened inside the container.

If the user needs to observe execution effects inside the container, the resolver should additionally enable one or more of the following, but only when justified by the request:

- host-visible output dirs
- command wrapper scripts
- task-runner execution paths

Enable host output dirs when the request implies:
- logs
- test results
- command output
- job output
- runtime inspection

Enable command wrapper scripts when:
- repeatable in-container commands are needed
- Claude is expected to run actions inside the container

Enable task-runner wrappers only when `task-runner` is active.

---

## 10.8 Rebuild-image rule

If `rebuild-image` is enabled, likely include:

- `compose.yml`
- `compose.rebuild.yml`

Do not automatically include:

- `compose.live.yml`
- host output dirs
- task-runner wrappers

unless separately justified.

### Rebuild-image observability rule

Rebuild-image changes how code reaches the container, but it does not by itself guarantee visibility into what happened inside the container.

If the user needs to observe execution effects inside the container, the resolver should additionally enable one or more of the following, but only when justified by the request:

- host-visible output dirs
- command wrapper scripts
- task-runner execution paths

Enable host output dirs when the request implies:
- logs
- test results
- command output
- job output
- runtime inspection

Enable command wrapper scripts when:
- repeatable in-container commands are needed
- Claude is expected to run actions inside the container

Enable task-runner wrappers only when `task-runner` is active.

---

# 11. Image Report Semantics

`image_report.py` must separate support from activation.

It should report:

- `roles_supported`
- `workflow_modes_supported`

And if a resolved plan exists:

- `roles_active`
- `workflow_modes_active`

Rules:

- support does not imply activation
- activation comes only from `resolved_plan`

---

# 12. Controller Flow

## 12.1 Draft generation flow

1. read repo cache
2. bootstrap if missing
3. build deterministic repo outputs
4. build deterministic draft packaging plan
5. write `packaging_plan.json`
6. write `image_selection_report.json`

## 12.2 Resolve packaging flow

1. read cache
2. ensure previous plan exists
3. validate required draft keys
4. rebuild fresh draft
5. compare fresh draft vs previous plan
6. mark stale if needed
7. classify request
8. decide lifecycle action
9. preserve / wipe / re-resolve
10. write `resolved_plan`
11. write `resolution_metadata`
12. generate only from `resolved_plan`

---

# 13. Testing Strategy

This section defines how to test each subsystem.

## 13.1 Test categories

- unit tests
- schema validation tests
- lifecycle tests
- integration tests
- regression tests

---

## 13.2 `common.py` tests

### Test: `build_error`
Input:
- code/message/recoverable/suggested_action

Expect:
- returned dict has all required keys
- optional `details` included only when present

### Test: `with_error_state`
Input:
- sample plan
- state + error payload

Expect:
- state updated
- error attached
- other plan content preserved

---

## 13.3 `artifact_rules.py` tests

### Test: Node / Next.js capability rules
Input:
- node nextjs target

Expect:
- `supports_compose = true`
- `supports_live_bind = true`
- `supports_rebuild_image = true`
- `supports_task_runner = true`
- `default_mode = live-bind`
- suggested artifacts include `Dockerfile`, `.dockerignore`, `compose.yml`

### Test: Python target rules
Input:
- python target

Expect:
- same schema shape
- runtime commands appropriate to python
- no missing required keys

### Test: Generic fallback rules
Input:
- unknown runtime

Expect:
- schema shape remains valid
- conservative suggestions only

---

## 13.4 `packaging_planner.py` tests

### Test: planner emits draft-only schema
Input:
- valid target and image candidates

Expect:
- `state = draft_only`
- `resolved_plan is None`
- required top-level keys present

### Test: planner does not emit active artifact generation fields
Expect absence of:
- `artifacts_to_generate`
- `enabled_roles`
- `enabled_modes`
- `compose_files`
- `command_scripts`
- `host_output_dirs`

### Test: `draft_hash` reproducibility
Run planner twice with identical inputs.

Expect:
- identical `draft_hash`

---

## 13.5 `plan_staleness.py` tests

### Test: unchanged draft is not stale
Input:
- identical fresh draft and previous plan
- same fingerprint

Expect:
- `False`
- empty reasons

### Test: changed target is stale
Change:
- `target_id`

Expect:
- stale
- reason contains `target_changed`

### Test: changed capability is stale
Change:
- `supports_task_runner`

Expect:
- stale
- reason contains `capabilities_changed`

### Test: changed default is stale
Change:
- `default_mode`

Expect:
- stale
- reason contains `defaults_changed`

### Test: changed fingerprint is stale
Change:
- fingerprint hash

Expect:
- stale
- reason contains `fingerprint_changed`

### Test: `mark_plan_stale`
Expect:
- `state = stale`
- structured `ERR_STALE_PLAN`

---

## 13.6 `request_lifecycle.py` tests

### Test: read-only classification
Input:
- "explain this plan"

Expect:
- `read_only`

### Test: production classification
Input:
- "just give me a production image"

Expect:
- `productionization`

### Test: isolated runtime classification
Input:
- "run tests in container only"

Expect:
- `isolated_runtime_request`

### Test: mode change classification
Input:
- "switch to live-bind"

Expect:
- `mode_change`

### Test: lifecycle preserve
Input:
- request class `read_only`

Expect:
- `preserve`

### Test: lifecycle wipe and re-resolve
Input:
- request class `new_packaging`

Expect:
- `wipe_and_reresolve`

### Test: lifecycle stale handling
Input:
- stale flag true + update request

Expect:
- deterministic action according to rule table

---

## 13.7 `plan_resolver.py` tests

### Test: minimal new packaging
Input:
- app-only defaults
- live-bind supported
- no explicit task-runner request

Expect:
- `enabled_roles = ["app"]`
- one mode
- minimal artifact set

### Test: productionization
Input:
- production request
- rebuild-image supported

Expect:
- `enabled_modes = ["rebuild-image"]`
- no task-runner by default
- no host output dirs by default

### Test: isolated runtime request
Input:
- task-runner supported

Expect:
- `enabled_roles = ["task-runner"]`
- task-runner wrappers included

### Test: unsupported task-runner
Input:
- request for task-runner
- capability false

Expect:
- structured `ERR_CAPABILITY_CONFLICT`

### Test: unsupported live-bind
Input:
- request for live-bind
- capability false

Expect:
- structured `ERR_INVALID_REQUEST_MODE`

---

## 13.8 Artifact derivation tests

### Test: live-bind derivation
Input:
- `enabled_modes = ["live-bind"]`

Expect:
- `compose.yml`
- `compose.live.yml`
- no `compose.rebuild.yml`

### Test: rebuild-image derivation
Input:
- `enabled_modes = ["rebuild-image"]`

Expect:
- `compose.yml`
- `compose.rebuild.yml`
- no `compose.live.yml`

### Test: task-runner derivation
Input:
- `enabled_roles = ["task-runner"]`

Expect:
- task-runner wrappers present

### Test: host output derivation
Input:
- isolated runtime request

Expect:
- `.docker-data/logs`
- `.docker-data/test-results`
- `.docker-data/command-output`

### Test: minimal production derivation
Input:
- production request

Expect:
- no host output dirs by default
- no task-runner wrappers by default
- minimal artifact set

---

## 13.9 `image_report.py` tests

### Test: support-only report
Input:
- draft plan with no resolved plan

Expect:
- `roles_supported` populated
- `workflow_modes_supported` populated
- `roles_active = []`
- `workflow_modes_active = []`

### Test: resolved report
Input:
- resolved plan exists

Expect:
- `roles_active` matches resolved plan
- `workflow_modes_active` matches resolved plan

### Test: fallback report
Input:
- MCP unavailable

Expect:
- `mcp_used = false`
- `fallback_used = true`

---

## 13.10 `project_detector.py` tests

### Test: bootstrap
Run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
```

Expect cache files:
- project facts
- graph
- targets
- fingerprint
- image candidates

### Test: draft planning
Run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
```

Expect:
- schema v3 draft
- no active artifact generation fields
- `resolved_plan = null`

### Test: image report
Run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
```

Expect:
- support-aware image report
- no false implication of activation

### Test: resolve packaging
Run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "just give me a production image"
```

Expect:
- `state = resolved`
- `resolved_plan` exists
- minimal production artifact set

### Test: stale re-resolution
1. create plan
2. change repo fingerprint materially
3. run `resolve-packaging`

Expect:
- stale detected
- fresh draft rebuilt
- new resolution written

---

## 13.11 End-to-end skill tests

### Test: full dockerize flow
Request:
- "dockerize this project"

Expect:
- cache read first
- draft exists
- resolver runs
- MCP image re-check happens
- only resolved artifacts written

### Test: Dockerfile-only flow
Request:
- "update Dockerfile only"

Expect:
- resolved scope honored
- no compose or Makefile generated

### Test: compose-only flow
Request:
- "update compose for live-bind"

Expect:
- resolver activates live-bind
- compose files only
- no unrelated artifacts

### Test: planning-only flow
Request:
- "refresh docker plan only"

Expect:
- draft plan refreshed
- image report refreshed
- no artifact generation

---

# 14. Success Criteria

The system is complete when it can reliably do all of the following:

- describe repo capabilities without overcommitting
- provide light defaults without forcing structure
- resolve only what the request actually needs
- preserve prior plans only when still valid
- detect stale plans deterministically
- reject unsupported requests explicitly
- avoid silent downgrades on important intent
- minimize structure when intent is vague
- generate only resolved artifacts
- explain where each decision came from
- report image support separately from active usage

---

# 15. Governing Principle

**Deterministic code should describe possibility. The resolver should decide activation.**
